import logging
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import or_
from sqlalchemy.orm import Session
import models, schemas
import parser
from database import engine, SessionLocal
import shutil
import os

# Создаем таблицы, если их нет
models.Base.metadata.create_all(bind=engine)

# Настройка логирования
LOG_FILE_PATH = "/var/www/article-app/logs/app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler() # Чтобы логи также писались в системный журнал
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Article Management API")

app.mount("/uploaded_files", StaticFiles(directory="uploaded_files"), name="uploaded_files")

origins = [
    "http://localhost:5173",  # Адрес, где работает ваш Vue.js при разработке
    "https://articles-app.ru", # Адрес вашего домена
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "API is working! Database models loaded."}

# Эндпоинт: Создать новый проект
@app.post("/projects/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(
        name=project.name, 
        description=project.description, 
        goals=project.goals
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# Эндпоинт: Получить список всех проектов
@app.get("/projects/", response_model=list[schemas.ProjectResponse])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

# Эндпоинт: Обновить проект
@app.put("/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    db_project.name = project.name
    db_project.description = project.description
    db_project.goals = project.goals
    db.commit()
    db.refresh(db_project)
    return db_project

# Эндпоинт: Удалить проект
@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Проект успешно удален"}

# Эндпоинт: Добавить новую статью
@app.post("/articles/", response_model=schemas.ArticleResponse)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    # .dict() превращает данные от пользователя в формат для базы данных
    db_article = models.Article(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

# Эндпоинт: Получить список всех статей
@app.get("/articles/", response_model=list[schemas.ArticleResponse])
def get_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = db.query(models.Article).offset(skip).limit(limit).all()
    return articles

# Эндпоинт: Обновить статью
@app.put("/articles/{article_id}", response_model=schemas.ArticleResponse)
def update_article(article_id: int, article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    
    # Обновляем все переданные поля
    for key, value in article.dict().items():
        setattr(db_article, key, value)
        
    db.commit()
    db.refresh(db_article)
    return db_article

# Эндпоинт: Удалить статью
@app.delete("/articles/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    
    db.delete(db_article)
    db.commit()
    return {"message": "Статья успешно удалена"}

# Эндпоинт: Создать тег
@app.post("/tags/", response_model=schemas.TagResponse)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    # Используем цвет из запроса или дефолтный
    db_tag = models.Tag(name=tag.name, color=tag.color or "#3498db")
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

# Эндпоинт: Обновить цвет тега
@app.put("/tags/{tag_id}", response_model=schemas.TagResponse)
def update_tag(tag_id: int, tag_data: schemas.TagCreate, db: Session = Depends(get_db)):
    db_tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Тег не найден")
    
    db_tag.name = tag_data.name
    db_tag.color = tag_data.color
    db.commit()
    db.refresh(db_tag)
    return db_tag

# Эндпоинт: Полностью удалить тег из базы данных
@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Тег не найден")
    
    # SQLAlchemy автоматически удалит связи из таблицы article_tags благодаря каскадам или foreign keys
    db.delete(db_tag)
    db.commit()
    return {"message": "Тег успешно удален из системы"}

# Эндпоинт: Отвязать тег от конкретной статьи (удалить связь, но сохранить сам тег в справочнике)
@app.delete("/articles/{article_id}/tags/{tag_id}")
def remove_tag_from_article(article_id: int, tag_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    
    if not article or not tag:
        raise HTTPException(status_code=404, detail="Статья или тег не найдены")
    
    # Если тег привязан к статье, удаляем его из списка связей
    if tag in article.tags:
        article.tags.remove(tag)
        db.commit()
        
    return {"message": "Тег успешно отвязан от статьи"}

# Эндпоинт: Получить список всех тегов
@app.get("/tags/", response_model=list[schemas.TagResponse])
def get_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tags = db.query(models.Tag).offset(skip).limit(limit).all()
    return tags

# # Эндпоинт: Привязать тег к статье
# @app.post("/articles/{article_id}/tags/{tag_id}")
# def add_tag_to_article(article_id: int, tag_id: int, db: Session = Depends(get_db)):
#     article = db.query(models.Article).filter(models.Article.id == article_id).first()
#     tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    
#     if not article or not tag:
#         return {"error": "Статья или тег не найдены"}
    
#     article.tags.append(tag)
#     db.commit()
#     return {"message": "Тег успешно привязан"}

# Эндпоинт: Добавить заметку к статье
@app.post("/articles/{article_id}/notes/", response_model=schemas.NoteResponse)
def create_note(article_id: int, note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = models.Note(article_id=article_id, **note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

# Эндпоинт: Получить все заметки к статье
@app.get("/articles/{article_id}/notes/", response_model=list[schemas.NoteResponse])
def get_notes(article_id: int, db: Session = Depends(get_db)):
    return db.query(models.Note).filter(models.Note.article_id == article_id).all()

# Эндпоинт: Обновить заметку
@app.put("/notes/{note_id}", response_model=schemas.NoteResponse)
def update_note(note_id: int, note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    
    db_note.field_type = note.field_type
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note

# Эндпоинт: Удалить заметку
@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    
    db.delete(db_note)
    db.commit()
    return {"message": "Заметка успешно удалена"}

# Эндпоинт: Поиск статей
@app.get("/search/")
def search_articles(query: str, db: Session = Depends(get_db)):
    # Ищем вхождение строки в название или абстракт
    results = db.query(models.Article).filter(
        or_(
            models.Article.title.ilike(f"%{query}%"),
            models.Article.abstract.ilike(f"%{query}%")
        )
    ).all()
    return results

# Эндпоинт: Создать драфт
@app.post("/drafts/")
def create_draft(project_id: int, title: str, db: Session = Depends(get_db)):
    db_draft = models.Draft(project_id=project_id, title=title)
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    return db_draft

# Эндпоинт: Получить драфт для конкретного проекта (или создать пустой, если его нет)
@app.get("/projects/{project_id}/draft", response_model=schemas.DraftResponse)
def get_or_create_project_draft(project_id: int, db: Session = Depends(get_db)):
    draft = db.query(models.Draft).filter(models.Draft.project_id == project_id).first()
    if not draft:
        # Если черновика еще не существовало для этого проекта — автоматически создаем его
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        title = f"Черновик: {project.name}" if project else "Новый черновик"
        draft = models.Draft(project_id=project_id, title=title, content="")
        db.add(draft)
        db.commit()
        db.refresh(draft)
    return draft

# Эндпоинт: Сохранить/обновить текст и заголовок драфта
@app.put("/drafts/{draft_id}")
def update_draft(draft_id: int, title: str, content: str, db: Session = Depends(get_db)):
    draft = db.query(models.Draft).filter(models.Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Черновик не найден")
    draft.title = title
    draft.content = content
    db.commit()
    return {"message": "Draft saved successfully"}

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-article/")
async def upload_article(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # --- НОВАЯ ЛОГИКА ИЗВЛЕЧЕНИЯ МЕТАДАННЫХ ---
    extracted_text = parser.extract_text_from_pdf(file_path)
    doi = parser.extract_doi_from_text(extracted_text)
    
    metadata = None
    if doi:
        metadata = parser.get_metadata_from_doi(doi)
        
    return {
        "filename": file.filename, 
        "path": file_path,
        "extracted_metadata": metadata # Возвращаем найденные данные на клиент
    }

# Эндпоинт: Создать автора в справочнике
@app.post("/authors/", response_model=schemas.AuthorResponse)
def create_author(author: schemas.AuthorBase, db: Session = Depends(get_db)):
    db_author = models.Author(last_name=author.last_name, initials=author.initials)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

# Эндпоинт: Получить список всех авторов
@app.get("/authors/", response_model=list[schemas.AuthorResponse])
def get_authors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Author).offset(skip).limit(limit).all()

# --- ЭНДПОИНТЫ ДЛЯ ЦИТАТ (Quotes) ---

# Эндпоинт: Сохранить новую цитату из статьи
@app.post("/quotes/", response_model=schemas.QuoteResponse)
def create_quote(quote: schemas.QuoteCreate, db: Session = Depends(get_db)):
    db_quote = models.Quote(**quote.dict())
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    return db_quote

# Эндпоинт: Получить все цитаты для конкретной статьи
@app.get("/articles/{article_id}/quotes/", response_model=list[schemas.QuoteResponse])
def get_quotes_by_article(article_id: int, db: Session = Depends(get_db)):
    return db.query(models.Quote).filter(models.Quote.article_id == article_id).all()

# Эндпоинт: Удалить цитату
@app.delete("/quotes/{quote_id}")
def delete_quote(quote_id: int, db: Session = Depends(get_db)):
    db_quote = db.query(models.Quote).filter(models.Quote.id == quote_id).first()
    if not db_quote:
        raise HTTPException(status_code=404, detail="Цитата не найдена")
    
    db.delete(db_quote)
    db.commit()
    return {"message": "Цитата успешно удалена"}

# --- ЭНДПОИНТЫ ДЛЯ ЦИТИРОВАНИЯ В ДРАФТЕ (Draft Citations) ---

# Эндпоинт: Привязать статью к маркеру в драфте
@app.post("/draft-citations/", response_model=schemas.DraftCitationResponse)
def create_draft_citation(citation: schemas.DraftCitationCreate, db: Session = Depends(get_db)):
    db_citation = models.DraftCitation(**citation.dict())
    db.add(db_citation)
    db.commit()
    db.refresh(db_citation)
    return db_citation

# Эндпоинт: Получить все привязанные статьи для конкретного драфта
@app.get("/drafts/{draft_id}/citations/", response_model=list[schemas.DraftCitationResponse])
def get_citations_by_draft(draft_id: int, db: Session = Depends(get_db)):
    return db.query(models.DraftCitation).filter(models.DraftCitation.draft_id == draft_id).all()

# Эндпоинт: Удалить привязку (если маркер удален из текста)
@app.delete("/draft-citations/{citation_id}")
def delete_draft_citation(citation_id: int, db: Session = Depends(get_db)):
    db_citation = db.query(models.DraftCitation).filter(models.DraftCitation.id == citation_id).first()
    if not db_citation:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    
    db.delete(db_citation)
    db.commit()
    return {"message": "Внутритекстовая ссылка успешно удалена"}

# --- ЭНДПОИНТЫ ДЛЯ СВЯЗИ АВТОРОВ И СТАТЕЙ ---

# Эндпоинт: Синхронизация авторов статьи (сохраняет порядок)
@app.post("/articles/{article_id}/sync-authors/")
def sync_article_authors(article_id: int, data: schemas.AuthorSync, db: Session = Depends(get_db)):
    # 1. Удаляем старые связи
    db.query(models.ArticleAuthor).filter(models.ArticleAuthor.article_id == article_id).delete()
    
    # 2. Записываем новые с правильным порядком (index + 1)
    for index, author_id in enumerate(data.author_ids):
        new_link = models.ArticleAuthor(
            article_id=article_id,
            author_id=author_id,
            order_index=index + 1
        )
        db.add(new_link)
    db.commit()
    return {"message": "Авторы успешно привязаны"}

# Эндпоинт: Получить список авторов конкретной статьи
@app.get("/articles/{article_id}/authors/")
def get_article_authors(article_id: int, db: Session = Depends(get_db)):
    links = db.query(models.ArticleAuthor).filter(models.ArticleAuthor.article_id == article_id).order_by(models.ArticleAuthor.order_index).all()
    result = []
    for link in links:
        author = db.query(models.Author).filter(models.Author.id == link.author_id).first()
        if author:
            result.append({
                "id": author.id,
                "last_name": author.last_name,
                "initials": author.initials
            })
    return result

# Эндпоинт: Привязать тег к статье (с защитой от дублей)
@app.post("/articles/{article_id}/tags/{tag_id}")
def add_tag_to_article(article_id: int, tag_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    
    if not article or not tag:
        raise HTTPException(status_code=404, detail="Статья или тег не найдены")
    
    # Защита от дубликатов: если тега еще нет у статьи, то добавляем
    if tag not in article.tags:
        article.tags.append(tag)
        db.commit()
        
    return {"message": "Тег успешно привязан"}

# Эндпоинт: Получить теги конкретной статьи
@app.get("/articles/{article_id}/tags/", response_model=list[schemas.TagResponse])
def get_article_tags(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return article.tags

# Эндпоинт: Сгенерировать цитату по стандарту APA
@app.get("/articles/{article_id}/apa")
def get_article_apa(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
        
    # Получаем авторов с учетом их порядка (order_index)
    links = db.query(models.ArticleAuthor).filter(models.ArticleAuthor.article_id == article_id).order_by(models.ArticleAuthor.order_index).all()
    authors = []
    for link in links:
        author = db.query(models.Author).filter(models.Author.id == link.author_id).first()
        if author:
            authors.append(f"{author.last_name}, {author.initials}")
            
    # Правило APA: перечисление авторов (через запятую, перед последним '&')
    if not authors:
        author_str = "Автор неизвестен."
    elif len(authors) == 1:
        author_str = f"{authors[0]}."
    elif len(authors) == 2:
        author_str = f"{authors[0]} & {authors[1]}."
    else:
        author_str = ", ".join(authors[:-1]) + f", & {authors[-1]}."
        
    # Год издания
    year_str = f"({article.year})." if article.year else "(н.д.)."
    
    # Название статьи/книги
    title_str = f"{article.title}."
    
    # Сборка основы
    citation = f"{author_str} {year_str} {title_str}"
    
    # Специфичные поля в зависимости от типа публикации
    if article.type == "Journal Article" and article.journal:
        citation += f" {article.journal},"
        if article.issue:
            citation += f" ({article.issue}),"
        if article.pages:
            citation += f" {article.pages}."
    elif article.type == "Book":
        if article.edition:
            citation += f" ({article.edition} ed.)."
            
    # Ссылки: DOI в приоритете, иначе Web Link
    if article.doi:
        doi_link = article.doi if article.doi.startswith("http") else f"https://doi.org/{article.doi}"
        citation += f" {doi_link}"
    elif article.web_link:
        citation += f" {article.web_link}"
        
    # Очищаем от лишних пробелов (на случай если какое-то поле пустое)
    import re
    citation = re.sub(' +', ' ', citation)
    
    return {"citation": citation.strip()}

# Эндпоинт: Сгенерировать внутритекстовую цитату (Author, Year)
@app.get("/articles/{article_id}/apa-in-text")
def get_article_apa_in_text(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    links = db.query(models.ArticleAuthor).filter(models.ArticleAuthor.article_id == article_id).order_by(models.ArticleAuthor.order_index).all()
    
    authors = []
    for link in links:
        author = db.query(models.Author).filter(models.Author.id == link.author_id).first()
        if author:
            authors.append(author.last_name)

    year_str = str(article.year) if article.year else "н.д."

    if not authors:
        author_str = "Автор неизвестен"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) == 2:
        author_str = f"{authors[0]} & {authors[1]}"
    else:
        author_str = f"{authors[0]} et al." # APA стандарт для 3+ авторов

    return {"in_text": f"({author_str}, {year_str})"}

# Эндпоинт: Умный глобальный поиск по всей базе
# Эндпоинт: Умный глобальный поиск по всей базе (теперь запрос передается в URL)
@app.get("/search/{q}")
def global_search(q: str, db: Session = Depends(get_db)):
    # Если запрос слишком короткий
    if not q or len(q) < 2:
        return {"articles": [], "drafts": [], "tags": []}

    search_pattern = f"%{q}%"

    # 1. Ищем статьи
    articles = db.query(models.Article).filter(
        or_(
            models.Article.title.ilike(search_pattern),
            models.Article.abstract.ilike(search_pattern)
        )
    ).limit(5).all()

    # 2. Ищем черновики
    drafts = db.query(models.Draft).filter(
        or_(
            models.Draft.title.ilike(search_pattern),
            models.Draft.content.ilike(search_pattern)
        )
    ).limit(5).all()

    # 3. Ищем теги
    tags = db.query(models.Tag).filter(
        models.Tag.name.ilike(search_pattern)
    ).limit(5).all()

    return {
        "articles": [{"id": a.id, "title": a.title, "year": a.year} for a in articles],
        "drafts": [{"id": d.id, "title": d.title, "project_id": d.project_id} for d in drafts],
        "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in tags]
    }

# Эндпоинт: Редактировать автора в глобальном справочнике
@app.put("/authors/{author_id}", response_model=schemas.AuthorResponse)
def update_author(author_id: int, author_data: schemas.AuthorCreate, db: Session = Depends(get_db)):
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Автор не найден")
    
    db_author.last_name = author_data.last_name
    db_author.initials = author_data.initials
    db.commit()
    db.refresh(db_author)
    return db_author

# Эндпоинт: Полностью удалить автора из базы данных
@app.delete("/authors/{author_id}")
def delete_author(author_id: int, db: Session = Depends(get_db)):
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Автор не найден")
    
    try:
        # 1. Сначала удаляем все привязки этого автора к статьям (чтобы БД не ругалась)
        db.query(models.ArticleAuthor).filter(models.ArticleAuthor.author_id == author_id).delete()
        
        # 2. Теперь спокойно удаляем самого автора
        db.delete(db_author)
        db.commit()
        return {"message": "Автор успешно удален из системы"}
    except Exception as e:
        db.rollback() # Откатываем транзакцию в случае любой непредвиденной ошибки
        logger.error(f"Ошибка БД при удалении автора {author_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка при удалении автора")
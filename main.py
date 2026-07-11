import logging
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
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

# Эндпоинт: Создать новый тег
@app.post("/tags/", response_model=schemas.TagResponse)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

# Эндпоинт: Получить список всех тегов
@app.get("/tags/", response_model=list[schemas.TagResponse])
def get_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tags = db.query(models.Tag).offset(skip).limit(limit).all()
    return tags

# Эндпоинт: Привязать тег к статье
@app.post("/articles/{article_id}/tags/{tag_id}")
def add_tag_to_article(article_id: int, tag_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    
    if not article or not tag:
        return {"error": "Статья или тег не найдены"}
    
    article.tags.append(tag)
    db.commit()
    return {"message": "Тег успешно привязан"}

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

# Эндпоинт: Сохранить/обновить текст драфта
@app.put("/drafts/{draft_id}")
def update_draft(draft_id: int, content: str, db: Session = Depends(get_db)):
    draft = db.query(models.Draft).filter(models.Draft.id == draft_id).first()
    draft.content = content
    db.commit()
    return {"message": "Draft saved"}

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
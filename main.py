from fastapi import FastAPI, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal
from fastapi import UploadFile, File
import shutil
import os

# Создаем таблицы, если их нет
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Article Management API")

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
    
    # Здесь можно вызвать функцию extract_text_from_pdf(file_path)
    return {"filename": file.filename, "path": file_path}
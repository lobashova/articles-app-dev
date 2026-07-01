from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal

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
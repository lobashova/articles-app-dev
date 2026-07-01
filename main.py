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
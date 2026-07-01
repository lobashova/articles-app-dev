from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Базовая схема проекта
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    goals: Optional[str] = None

# Схема для создания проекта (наследует базовую)
class ProjectCreate(ProjectBase):
    pass

# Схема ответа (то, что сервер возвращает клиенту)
class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True # Позволяет Pydantic работать с моделями SQLAlchemy

# --- СХЕМЫ ДЛЯ СТАТЕЙ ---
class ArticleBase(BaseModel):
    type: str
    title: str
    year: Optional[int] = None
    pdf_path: Optional[str] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    web_link: Optional[str] = None
    journal: Optional[str] = None
    issue: Optional[str] = None
    edition: Optional[str] = None
    pages: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleResponse(ArticleBase):
    id: int

    class Config:
        from_attributes = True

# --- СХЕМЫ ДЛЯ ТЕГОВ ---
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True
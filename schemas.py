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
    color: Optional[str] = "#3498db" # Добавьте это поле

class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True

# --- ЗАМЕТКИ ---
class NoteBase(BaseModel):
    field_type: str  # 'aims', 'methods', 'results', etc.
    content: str

class NoteCreate(NoteBase):
    pass

class NoteResponse(NoteBase):
    id: int
    article_id: int

    class Config:
        from_attributes = True

# --- АВТОРЫ ---
class AuthorBase(BaseModel):
    last_name: str
    initials: str

class AuthorResponse(AuthorBase):
    id: int

    class Config:
        from_attributes = True

# --- ЦИТАТЫ (Quotes) ---
class QuoteBase(BaseModel):
    highlighted_text: str
    page_number: Optional[int] = None

class QuoteCreate(QuoteBase):
    article_id: int

class QuoteResponse(QuoteBase):
    id: int
    article_id: int

    class Config:
        from_attributes = True

# --- ЦИТИРОВАНИЕ В ДРАФТЕ (Draft Citations) ---
class DraftCitationBase(BaseModel):
    in_text_marker: str

class DraftCitationCreate(DraftCitationBase):
    draft_id: int
    article_id: int

class DraftCitationResponse(DraftCitationBase):
    id: int
    draft_id: int
    article_id: int

    class Config:
        from_attributes = True

class AuthorSync(BaseModel):
    author_ids: list[int]

class DraftResponse(BaseModel):
    id: int
    project_id: int
    title: str
    content: Optional[str] = ""

    class Config:
        from_attributes = True
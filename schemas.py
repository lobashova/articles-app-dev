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
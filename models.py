from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Таблица связи для Тегов и Статей
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

# Таблица связи для Проектов и Статей
project_articles = Table(
    "project_articles",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("article_id", ForeignKey("articles.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    goals = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False, index=True)
    year = Column(Integer, nullable=True)
    pdf_path = Column(String, nullable=True)
    abstract = Column(Text, nullable=True)
    doi = Column(String, nullable=True)
    web_link = Column(String, nullable=True)
    journal = Column(String, nullable=True)
    issue = Column(String, nullable=True)
    edition = Column(String, nullable=True)
    pages = Column(String, nullable=True)
    tags = relationship("Tag", secondary=article_tags, backref="articles")
    projects = relationship("Project", secondary=project_articles, backref="articles")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    color = Column(String, default="#3498db") # Добавили поле цвета


class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    field_type = Column(String)  # Например: 'aims', 'methods', 'results'
    content = Column(Text)

class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String, index=True, nullable=False)
    initials = Column(String, nullable=False)

class ArticleAuthor(Base):
    __tablename__ = "article_authors"
    
    article_id = Column(Integer, ForeignKey("articles.id"), primary_key=True)
    author_id = Column(Integer, ForeignKey("authors.id"), primary_key=True)
    order_index = Column(Integer)  # Порядок автора (1-й, 2-й...)

class Draft(Base):
    __tablename__ = "drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True) # Здесь будет ваш Markdown-текст

class Quote(Base):
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    highlighted_text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)

class DraftCitation(Base):
    __tablename__ = "draft_citations"
    
    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("drafts.id"))
    article_id = Column(Integer, ForeignKey("articles.id"))
    in_text_marker = Column(String, nullable=False)
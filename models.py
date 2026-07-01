from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

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

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
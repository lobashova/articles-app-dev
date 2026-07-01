import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем ссылку на базу данных
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем "движок" для подключения
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем фабрику сессий для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс, от которого будут наследоваться наши модели
Base = declarative_base()
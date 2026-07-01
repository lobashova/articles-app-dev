from fastapi import FastAPI
import models
from database import engine

# Эта команда создает все таблицы в БД, если их еще нет
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Article Management API")

@app.get("/")
def read_root():
    return {"message": "API is working! Database models loaded."}
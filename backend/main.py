# backend/main.py
import os
from typing import Generator, List
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import telebot
from database import Base, engine, SessionLocal
import models

Base.metadata.create_all(bind=engine)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

app = FastAPI()

def _split_env_list(v: str | None) -> list[str]:
    if not v:
        return []
    return [x.strip() for x in v.split(",") if x.strip()]

allow_origins = _split_env_list(os.getenv("CORS_ORIGINS"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ApplicationForm(BaseModel):
    name: str
    phone: str

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/submit")
def submit(form: ApplicationForm, db: Session = Depends(get_db)):
    application = models.Application(name=form.name, phone=form.phone)
    db.add(application)
    db.commit()
    db.refresh(application)

    if bot and CHAT_ID:
        try:
            bot.send_message(CHAT_ID, f"📥 Новая заявка!\n\nИмя: {form.name}\nТелефон: {form.phone}")
        except Exception as e:
            print("Telegram error:", e)

    return {"status": "success", "id": application.id}

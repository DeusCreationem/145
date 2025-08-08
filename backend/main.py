import os
from typing import Generator, List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

import telebot
from database import Base, engine, SessionLocal
import models

# --- DB ---
Base.metadata.create_all(bind=engine)

# --- Telegram ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")

bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

# --- App ---
app = FastAPI()

# --- CORS ---
def _split_env_list(v: str | None) -> List[str]:
    if not v:
        return []
    return [x.strip() for x in v.split(",") if x.strip()]

allow_origins = _split_env_list(os.getenv("CORS_ORIGINS"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins or ["*"],  # подожми позже, когда всё заведётся
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---
class ApplicationForm(BaseModel):
    name: str
    phone: str

# --- DI ---
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Routes ---
@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/submit")
def submit(form: ApplicationForm, db: Session = Depends(get_db)):
    application = models.Application(name=form.name, phone=form.phone)
    db.add(application)
    db.commit()
    db.refresh(application)

    if bot and CHAT_ID:
        msg = f"📥 Новая заявка!\n\nИмя: {form.name}\nТелефон: {form.phone}"
        try:
            bot.send_message(CHAT_ID, msg)
        except Exception as e:
            # не валим запрос, если телега офлайн
            print("Telegram error:", e)

    return {"status": "success", "id": application.id}

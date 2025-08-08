import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

PG_USER = os.getenv("PG_USER", "wb_user")
PG_PASSWORD = os.getenv("PG_PASSWORD", "password")
PG_DB = os.getenv("PG_DB", "wb_bot_db")
PG_HOST = os.getenv("PG_HOST", "db")  # имя сервиса БД в compose

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:5432/{PG_DB}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()

# app/core/dependencies.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings
from typing import Generator
from datetime import datetime # [cite: 182]

# Database setup
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# app/core/utils.py
def parse_date_string(date_str: str) -> datetime:
    """Parses a date string into a datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d")
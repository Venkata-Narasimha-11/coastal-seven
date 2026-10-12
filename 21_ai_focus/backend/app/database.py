"""SQLAlchemy database engine, session factory, and base model configuration."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Engine configuration with appropriate connection arguments
connect_args = {"check_same_thread": False} if settings.USE_SQLITE_FALLBACK else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_size=settings.DB_POOL_SIZE if not settings.USE_SQLITE_FALLBACK else 5,
    max_overflow=settings.DB_MAX_OVERFLOW if not settings.USE_SQLITE_FALLBACK else 10,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields an independent database session and safely closes it."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

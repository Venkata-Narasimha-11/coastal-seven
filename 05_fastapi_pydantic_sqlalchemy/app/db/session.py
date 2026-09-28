"""SQLAlchemy 2.0 Async Engine and Async Session Management."""

import logging
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger("FastAPIStore.Database")

# Create AsyncEngine using asyncpg dialect
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DB_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

# AsyncSession factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an isolated transactional AsyncSession.
    
    Commits on successful completion of the request and rolls back on unhandled error.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Database session rolled back due to error: %s", e)
            raise
        finally:
            await session.close()


async def check_database_connection() -> bool:
    """Lightweight health check executing a SELECT 1 query through the async engine."""
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1;"))
            scalar = result.scalar()
            return scalar == 1
    except Exception as e:
        logger.warning("Database connection check failed: %s", e)
        return False

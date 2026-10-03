"""Async database engine and session factory for Day 7."""

import logging
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger("TaskManagementAPI.Database")

# Engine connection kwargs depending on driver
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "future": True,
}

if settings.async_database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
    })

async_engine = create_async_engine(
    settings.async_database_url,
    **engine_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency generating isolated transactional AsyncSession."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Transaction rolled back due to exception: %s", e)
            raise
        finally:
            await session.close()


async def check_database_connection() -> bool:
    """Performs lightweight ping to verify database availability."""
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1;"))
            return result.scalar() == 1
    except Exception as e:
        logger.warning("Database connectivity check failed: %s", e)
        return False

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
from app.core.config import settings
from app.core.logging import logger

# Ensure database directory exists if using SQLite
if "sqlite" in settings.DATABASE_URL:
    db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

# Build engine with connection pooling options suitable for sqlite/postgres
engine_kwargs = {"echo": False, "future": True}
if "sqlite" in settings.DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining async DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables and extensions."""
    # Ensure upload directory exists
    if not os.path.exists(settings.UPLOAD_DIR):
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    async with engine.begin() as conn:
        if "postgresql" in settings.DATABASE_URL:
            try:
                # Enable pgvector extension if postgresql
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                logger.info("pgvector extension verified/created on PostgreSQL.")
            except Exception as e:
                logger.warning(f"Could not enable pgvector extension: {e}")
        
        # Create all tables defined in models
        import app.models
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized successfully.")

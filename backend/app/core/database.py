from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from backend.app.core.config import settings

# Engine setup
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}, # Needed for SQLite
)

# Session factory
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)

# Base class for models
class Base(DeclarativeBase):
    pass

# Dependency to get db session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

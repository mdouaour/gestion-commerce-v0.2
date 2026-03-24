import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
import os
import asyncio

# Use a test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_app.db"

engine_test = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    if os.path.exists("./test_app.db"):
        os.remove("./test_app.db")

@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.close()

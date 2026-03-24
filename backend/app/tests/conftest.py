import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base, get_db
import os
import asyncio
from httpx import AsyncClient
from app.main import app
from sqlalchemy import delete
from app.models.finance import CashRegister, CashTransaction, Withdrawal
from app.models.user import User
from app.models.product import Product, Category
from app.models.base import StockHistory

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

@pytest.fixture(autouse=True)
async def clean_db(db_session):
    # This runs before every test to ensure isolation
    yield
    await db_session.execute(delete(CashTransaction))
    await db_session.execute(delete(Withdrawal))
    await db_session.execute(delete(CashRegister))
    await db_session.execute(delete(StockHistory))
    await db_session.execute(delete(Product))
    await db_session.execute(delete(Category))
    await db_session.execute(delete(User))
    await db_session.commit()

@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.close()

@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

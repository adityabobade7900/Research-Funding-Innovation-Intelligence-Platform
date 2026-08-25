import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base
from app.core.deps import get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# Use isolated in-memory SQLite database for test execution
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)




@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    """Initializes tables before each test and drops them afterward."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency override providing an isolated test session."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provides an AsyncClient for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user() -> dict:
    """Inserts a default test user directly into the database."""
    async with TestingSessionLocal() as session:
        user = User(
            email="researcher@university.edu",
            hashed_password=get_password_hash("StrongPassword123!"),
            full_name="Dr. Elena Vance",
            role=UserRole.RESEARCHER,
            is_active=True,
            is_superuser=False
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return {
            "id": user.id,
            "email": user.email,
            "password": "StrongPassword123!",
            "full_name": user.full_name,
            "role": user.role.value
        }

import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import jwt
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.session import get_db
from app.main import app
from app.models.base import Base

# Use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def test_supabase_user_id() -> uuid.UUID:
    """Generate a test Supabase user ID."""
    return uuid.uuid4()


@pytest.fixture(scope="session")
def test_jwt_secret() -> str:
    """Test JWT secret."""
    return "test-secret-key-for-testing-only"


@pytest.fixture
def valid_token(test_supabase_user_id: uuid.UUID, test_jwt_secret: str) -> str:
    """Generate a valid test JWT token."""
    payload = {
        "aud": "authenticated",
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
        "iss": "https://test-project.supabase.co/auth/v1",
        "sub": str(test_supabase_user_id),
        "email": "test@example.com",
        "role": "authenticated",
        "app_metadata": {"provider": "email"},
        "user_metadata": {},
    }
    return jwt.encode(payload, test_jwt_secret, algorithm="HS256")


@pytest.fixture
def expired_token(test_supabase_user_id: uuid.UUID, test_jwt_secret: str) -> str:
    """Generate an expired test JWT token."""
    payload = {
        "aud": "authenticated",
        "exp": datetime.now(UTC) - timedelta(hours=1),
        "iat": datetime.now(UTC) - timedelta(hours=2),
        "iss": "https://test-project.supabase.co/auth/v1",
        "sub": str(test_supabase_user_id),
        "email": "test@example.com",
        "role": "authenticated",
    }
    return jwt.encode(payload, test_jwt_secret, algorithm="HS256")


@pytest_asyncio.fixture
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(
    test_session: AsyncSession,
    test_jwt_secret: str,
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden dependencies."""

    async def override_get_db():
        yield test_session

    # Override settings for testing
    original_secret = settings.supabase_jwt_secret
    settings.supabase_jwt_secret = test_jwt_secret

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
    settings.supabase_jwt_secret = original_secret

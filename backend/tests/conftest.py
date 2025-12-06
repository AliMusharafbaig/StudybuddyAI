"""
StudyBuddy AI - Test Configuration
===================================
Pytest configuration and fixtures.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from main import app
from core.database import Base, get_db
from core.config import settings


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_studybuddy.db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)





@pytest.fixture(scope="function")
async def setup_database():
    """Setup test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for tests."""
    async with test_session_maker() as session:
        yield session


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Get test database session."""
    async with test_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(setup_database) -> AsyncGenerator[AsyncClient, None]:
    """Get test client."""
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


import uuid

@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "email": f"test_{uuid.uuid4()}@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }


@pytest.fixture
def test_course_data():
    """Test course data."""
    return {
        "name": "Test Course",
        "description": "A test course",
        "code": "TEST101",
        "color": "#6366F1"
    }

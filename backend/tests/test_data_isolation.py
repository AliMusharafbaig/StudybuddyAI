import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from api.models.user import User
from api.models.course import Course
from api.middleware.auth import get_password_hash

# Fixtures for two users
@pytest.fixture
async def user_a(db_session: AsyncSession):
    user = User(
        email="usera@example.com",
        full_name="User A",
        hashed_password=get_password_hash("passwordA")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def user_b(db_session: AsyncSession):
    user = User(
        email="userb@example.com",
        full_name="User B",
        hashed_password=get_password_hash("passwordB")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def token_a(user_a, client):
    response = await client.post("/auth/login", data={"username": "usera@example.com", "password": "passwordA"})
    return response.json()["access_token"]

@pytest.fixture
async def token_b(user_b, client):
    response = await client.post("/auth/login", data={"username": "userb@example.com", "password": "passwordB"})
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_course_isolation(client: AsyncClient, token_a, token_b, db_session):
    # 1. User A creates a course
    response = await client.post(
        "/courses",
        json={"name": "User A Course", "description": "Private", "code": "CS101"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert response.status_code == 201
    course_a_id = response.json()["id"]

    # 2. User B tries to list courses - should NOT see User A's course
    response = await client.get("/courses", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 200
    courses_b = response.json()
    assert len(courses_b) == 0  # Should be empty for new user B

    # 3. User B tries to get User A's course specifically
    response = await client.get(f"/courses/{course_a_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 404  # Should be Not Found (security through obscurity)

@pytest.mark.asyncio
async def test_chat_isolation(client: AsyncClient, token_a, token_b):
    # 1. User A starts a chat
    response = await client.post(
        "/chat/message",
        json={"message": "Secret info only for A"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert response.status_code == 200
    
    # 2. User B asks for "Secret info" - should get generic response, not User A's context
    # (Note: we can't easily test RAG context without filling vector store, 
    # but we can test chat history isolation)
    
    response = await client.get("/chat/history", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 200
    history_b = response.json()
    assert len(history_b) == 0  # User B has no history

@pytest.mark.asyncio
async def test_update_other_user_course(client: AsyncClient, token_a, token_b):
    # 1. User A creates a course
    response = await client.post(
        "/courses",
        json={"name": "User A Course", "description": "Private", "code": "CS101"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    course_a_id = response.json()["id"]

    # 2. User B tries to update it
    response = await client.put(
        f"/courses/{course_a_id}",
        json={"name": "Hacked Course"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 404

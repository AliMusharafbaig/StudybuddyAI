"""
StudyBuddy AI - Course Tests
=============================
Unit and integration tests for course endpoints.
"""

import pytest
from httpx import AsyncClient


class TestCourseEndpoints:
    """Test course management endpoints."""

    async def get_auth_headers(self, client: AsyncClient, test_user_data) -> dict:
        """Helper to get auth headers."""
        response = await client.post("/api/auth/register", json=test_user_data)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_create_course(self, client: AsyncClient, test_user_data, test_course_data):
        """Test course creation."""
        headers = await self.get_auth_headers(client, test_user_data)
        response = await client.post("/api/courses", json=test_course_data, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_course_data["name"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_courses(self, client: AsyncClient, test_user_data, test_course_data):
        """Test listing courses."""
        headers = await self.get_auth_headers(client, test_user_data)
        # Create a course
        await client.post("/api/courses", json=test_course_data, headers=headers)
        # List courses
        response = await client.get("/api/courses", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    @pytest.mark.asyncio
    async def test_get_course(self, client: AsyncClient, test_user_data, test_course_data):
        """Test getting single course."""
        headers = await self.get_auth_headers(client, test_user_data)
        create_response = await client.post("/api/courses", json=test_course_data, headers=headers)
        course_id = create_response.json()["id"]
        
        response = await client.get(f"/api/courses/{course_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == course_id

    @pytest.mark.asyncio
    async def test_update_course(self, client: AsyncClient, test_user_data, test_course_data):
        """Test updating course."""
        headers = await self.get_auth_headers(client, test_user_data)
        create_response = await client.post("/api/courses", json=test_course_data, headers=headers)
        course_id = create_response.json()["id"]
        
        update_data = {"name": "Updated Course Name"}
        response = await client.put(f"/api/courses/{course_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Course Name"

    @pytest.mark.asyncio
    async def test_delete_course(self, client: AsyncClient, test_user_data, test_course_data):
        """Test deleting course."""
        headers = await self.get_auth_headers(client, test_user_data)
        create_response = await client.post("/api/courses", json=test_course_data, headers=headers)
        course_id = create_response.json()["id"]
        
        response = await client.delete(f"/api/courses/{course_id}", headers=headers)
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_course_not_found(self, client: AsyncClient, test_user_data):
        """Test accessing non-existent course."""
        headers = await self.get_auth_headers(client, test_user_data)
        response = await client.get("/api/courses/non-existent-id", headers=headers)
        assert response.status_code == 404

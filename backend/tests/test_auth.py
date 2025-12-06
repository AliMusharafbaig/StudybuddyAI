"""
StudyBuddy AI - Authentication Tests
======================================
Unit and integration tests for auth endpoints.
"""

import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, test_user_data):
        """Test successful user registration."""
        response = await client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == test_user_data["email"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user_data):
        """Test registration with duplicate email."""
        # First registration
        await client.post("/api/auth/register", json=test_user_data)
        # Second registration with same email
        response = await client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user_data):
        """Test successful login."""
        # Register first
        await client.post("/api/auth/register", json=test_user_data)
        # Login
        response = await client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user_data):
        """Test login with wrong password."""
        await client.post("/api/auth/register", json=test_user_data)
        response = await client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, test_user_data):
        """Test getting current user profile."""
        # Register and get token
        reg_response = await client.post("/api/auth/register", json=test_user_data)
        token = reg_response.json()["access_token"]
        
        # Get profile
        response = await client.get(
            "/api/auth/user",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == test_user_data["email"]

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized access to protected endpoint."""
        response = await client.get("/api/auth/user")
        assert response.status_code in [401, 403]

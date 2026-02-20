import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthAPI:
    async def test_register_success(self, test_client: AsyncClient):
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "full_name": "Name",
                "password": "securepass123",
            },
        )
        assert response.status_code == 201

    async def test_register_without_name(self, test_client: AsyncClient):
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser2@example.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == 201

    async def test_register_short_pass(self, test_client: AsyncClient):
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "full_name": "New User",
                "password": "shorty",
            },
        )
        assert response.status_code == 422
        assert "String should have at least" in response.json()["detail"][0]["msg"]

    async def test_register_wrong_email(self, test_client: AsyncClient):
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser",
                "full_name": "Name",
                "password": "securepass123",
            },
        )
        assert response.status_code == 422
        assert (
            "value is not a valid email address" in response.json()["detail"][0]["msg"]
        )

    async def test_register_duplicate_email(self, test_client: AsyncClient, test_user):
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "full_name": "DuplicateName",
                "password": "securepass123",
            },
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    async def test_login_success(self, test_client: AsyncClient, test_user):
        response = await test_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "ЯНастоящийЛёва",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, test_client: AsyncClient):
        response = await test_client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    async def test_refresh_token_success(self, test_client: AsyncClient, test_user):
        login_response = await test_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "ЯНастоящийЛёва",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Обновляем токен
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_token_invalid(self, test_client: AsyncClient):
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

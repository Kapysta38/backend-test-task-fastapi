import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUserAPI:
    async def test_get_current_user(self, test_client: AsyncClient, test_user):
        login_response = await test_client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": "ЯНастоящийЛёва"},
        )
        token = login_response.json()["access_token"]

        response = await test_client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email

    async def test_get_current_user_fake_token(
        self, test_client: AsyncClient, test_user
    ):
        response = await test_client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer faketoken"},
        )
        assert response.status_code == 401

    async def test_get_current_user_unauthorized(self, test_client: AsyncClient):
        response = await test_client.get("/api/v1/users/me")
        assert response.status_code == 401

    async def test_change_user_role_as_admin(
        self, test_client: AsyncClient, admin_user, test_user
    ):
        login_response = await test_client.post(
            "/api/v1/auth/login",
            data={"username": admin_user.email, "password": "топсикретпассворд"},
        )
        token = login_response.json()["access_token"]

        response = await test_client.post(
            "/api/v1/users/change",
            json={"role": "admin"},
            params={"email": test_user.email},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"

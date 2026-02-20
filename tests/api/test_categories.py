import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCategoryAPI:
    async def test_get_categories_empty(self, test_client: AsyncClient):
        response = await test_client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    async def test_get_categories_with_pagination(
        self, test_client: AsyncClient, test_category
    ):
        response = await test_client.get(
            "/api/v1/categories",
            params={"page": 1, "size": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["name"] == test_category.name

    async def test_create_category_as_admin(self, test_client: AsyncClient, admin_user):
        login_response = await test_client.post(
            "/api/v1/auth/login",
            data={"username": admin_user.email, "password": "топсикретпассворд"},
        )
        token = login_response.json()["access_token"]

        response = await test_client.post(
            "/api/v1/categories",
            json={"name": "New Category"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Category"
        assert "slug" in data

    async def test_create_category_as_user_forbidden(
        self, test_client: AsyncClient, test_user
    ):
        login_response = await test_client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": "ЯНастоящийЛёва"},
        )
        token = login_response.json()["access_token"]

        response = await test_client.post(
            "/api/v1/categories",
            json={"name": "Unauthorized Category"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_delete_category_not_found(
        self, test_client: AsyncClient, admin_user
    ):
        login_response = await test_client.post(
            "/api/v1/auth/login",
            data={"username": admin_user.email, "password": "топсикретпассворд"},
        )
        token = login_response.json()["access_token"]

        response = await test_client.delete(
            "/api/v1/categories/00000000",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

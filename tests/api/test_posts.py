import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestPostAPI:
    async def test_get_posts_empty(self, test_client: AsyncClient):
        response = await test_client.get("/api/v1/posts")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_get_post_by_slug(self, test_client: AsyncClient, test_post):
        response = await test_client.get(f"/api/v1/posts/{test_post.slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == test_post.title
        assert data["content_html"] == test_post.content_html

    async def test_get_post_not_found(self, test_client: AsyncClient):
        response = await test_client.get("/api/v1/posts/nonexistent-slug")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_create_post_as_admin(
        self, test_client: AsyncClient, admin_user, test_category
    ):
        login_response = await test_client.post(
            "/api/v1/auth/login",
            data={"username": admin_user.email, "password": "топсикретпассворд"},
        )
        token = login_response.json()["access_token"]

        response = await test_client.post(
            "/api/v1/posts",
            json={
                "title": "New Post",
                "content_html": "<p>Post content</p>",
                "category_id": str(test_category.id),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Post"
        assert "slug" in data

    async def test_delete_post_as_admin(
        self, test_client: AsyncClient, admin_user, test_post
    ):
        login_response = await test_client.post(
            "/api/v1/auth/login",
            data={"username": admin_user.email, "password": "топсикретпассворд"},
        )
        token = login_response.json()["access_token"]

        response = await test_client.delete(
            f"/api/v1/posts/{test_post.slug}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_post.id)

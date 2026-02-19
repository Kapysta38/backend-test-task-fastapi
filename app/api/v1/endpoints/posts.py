import uuid
from collections.abc import Sequence
from math import ceil
from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query

from app.api.deps import AdminUser, PostServiceDep, SessionDep
from app.core.constants import OrderDirection
from app.models.post import Post
from app.schemas.pagination import Page
from app.schemas.post import PostContent, PostCreate, PostPublic, PostUpdate

router = APIRouter()


@router.get("", response_model=Page[PostPublic])
async def get_posts(
    session: SessionDep,
    service: PostServiceDep,
    page: int = Query(1, ge=1, le=10000),
    order_by: Literal["title", "date_created"] = Query(
        "date_created", description="Поле сортировки: title, date_created"
    ),
    size: int = Query(
        20, ge=1, le=100, description="Размер постов в запросе (Максимум 100)"
    ),
    order_dir: OrderDirection = Query(
        OrderDirection.ASC, description="Направление сортировки"
    ),
) -> dict[str, Sequence[Post] | int]:
    """
    Получение всех постов постранично, а так же с выбранной сортировкой
    """
    column = service.POST_ORDER_FIELDS.get(order_by)
    if not column:
        raise HTTPException(
            status_code=400,
            detail=f"This column is not sortable or does not exist: {order_by}",
        )
    items, total = await service.paginate(
        session=session,
        page=page,
        size=size,
        order_by=column,
        order_dir=order_dir,
    )
    pages = ceil(total / size) if total else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
    }


@router.get("/{slug}", response_model=PostContent)
async def get_post(
    slug: str,
    session: SessionDep,
    service: PostServiceDep,
) -> Post:
    """
    Получение детальной информации о конкретном посте по slug
    """
    post = await service.get_by(session, service.model.slug, slug)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.post("", response_model=PostContent)
async def create_post(
    post_in: PostCreate, session: SessionDep, service: PostServiceDep, _: AdminUser
) -> Post:
    post = await service.create(session, post_in)
    return post


@router.put("/{identifier}", response_model=PostContent)
async def update_post(
    session: SessionDep,
    service: PostServiceDep,
    _: AdminUser,
    post_in: PostUpdate,
    identifier: str = Path(..., description="UUID или slug поста"),
) -> Post:
    # TODO: Добавить также обновление slug
    try:
        post_id = uuid.UUID(identifier)
        post = await service.get(session, post_id)
    except ValueError:
        post = await service.get_by(session, service.model.slug, identifier)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post = await service.update(session, post, post_in)
    return post


@router.delete("/{identifier}", response_model=PostContent)
async def delete_post(
    session: SessionDep,
    service: PostServiceDep,
    _: AdminUser,
    identifier: str = Path(..., description="UUID или slug поста"),
) -> Post | None:
    try:
        post_id = uuid.UUID(identifier)
        post = await service.get(session, post_id)
    except ValueError:
        post = await service.get_by(session, service.model.slug, identifier)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post = await service.remove(session, post.id)
    return post

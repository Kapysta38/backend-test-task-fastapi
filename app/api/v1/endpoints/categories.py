import uuid
from collections.abc import Sequence
from math import ceil
from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query

from app.api.deps import AdminUser, CategoryServiceDep, PostServiceDep, SessionDep
from app.core.constants import OrderDirection
from app.models.category import Category
from app.models.post import Post
from app.schemas.category import CategoryCreate, CategoryPublic, CategoryUpdate
from app.schemas.pagination import Page
from app.schemas.post import PostPublic

router = APIRouter()


@router.get("", response_model=Page[CategoryPublic])
async def get_categories(
    session: SessionDep,
    service: CategoryServiceDep,
    page: int = Query(1, ge=1, le=10000),
    order_by: Literal["name", "date_created"] = Query(
        "date_created", description="Поле сортировки: name, date_created"
    ),
    size: int = Query(
        20, ge=1, le=100, description="Размер постов в запросе (Максимум 100)"
    ),
    order_dir: OrderDirection = Query(
        OrderDirection.ASC, description="Направление сортировки"
    ),
) -> dict[str, Sequence[Category] | int]:
    """
    Получение всех категорий постранично
    """
    column = service.CATEGORY_ORDER_FIELDS.get(order_by)
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


@router.get("/{slug}/posts", response_model=Page[PostPublic])
async def get_posts_for_category(
    slug: str,
    session: SessionDep,
    post_service: PostServiceDep,
    category_service: CategoryServiceDep,
    page: int = Query(1, ge=1, le=10000),
    size: int = Query(
        20, ge=1, le=100, description="Размер постов в запросе (Максимум 100)"
    ),
) -> dict[str, Sequence[Post] | int]:
    """
    Получение списка постов для конкретной категории
    """
    category = await category_service.get_by(session, category_service.model.slug, slug)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    items, total = await post_service.paginate(
        session,
        post_service.model.category_id == category.id,
        page=page,
        size=size,
        order_by=post_service.model.date_created,
    )

    pages = ceil(total / size) if total else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
    }


@router.post("", response_model=CategoryPublic)
async def create_category(
    category_in: CategoryCreate,
    session: SessionDep,
    service: CategoryServiceDep,
    _: AdminUser,
) -> Category:
    """
    Создание категории
    """
    existing_category = await service.get_by(
        session, service.model.name, category_in.name
    )
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    category = await service.create(session, category_in)
    return category


@router.get("/{identifier}", response_model=CategoryPublic)
async def get_category(
    session: SessionDep,
    service: CategoryServiceDep,
    _: AdminUser,
    identifier: str = Path(..., description="UUID или slug поста"),
) -> Category:
    """
    Получение категории по UUID или slug
    """
    try:
        category_id = uuid.UUID(identifier)
        category = await service.get(session, category_id)
    except ValueError:
        category = await service.get_by(session, service.model.slug, identifier)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


@router.put("/{identifier}", response_model=CategoryPublic)
async def update_category(
    session: SessionDep,
    service: CategoryServiceDep,
    _: AdminUser,
    category_in: CategoryUpdate,
    identifier: str = Path(..., description="UUID или slug поста"),
) -> Category:
    """
    Обновление названия категории по UUID или slug
    """
    # TODO: Добавить также обновление slug
    try:
        category_id = uuid.UUID(identifier)
        category = await service.get(session, category_id)
    except ValueError:
        category = await service.get_by(session, service.model.slug, identifier)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category = await service.update(session, category, category_in)
    return category


@router.delete("/{identifier}", response_model=CategoryPublic)
async def delete_category(
    session: SessionDep,
    service: CategoryServiceDep,
    _: AdminUser,
    identifier: str = Path(..., description="UUID или slug поста"),
) -> Category | None:
    """
    Удаление категории по UUID или slug
    """
    try:
        category_id = uuid.UUID(identifier)
        category = await service.get(session, category_id)
    except ValueError:
        category = await service.get_by(session, service.model.slug, identifier)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category = await service.remove(session, category.id)
    return category

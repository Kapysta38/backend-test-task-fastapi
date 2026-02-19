from fastapi import APIRouter, HTTPException, Query
from pydantic import EmailStr

from app.api.deps import AdminUser, CurrentUser, SessionDep, UserServiceDep
from app.models.user import User
from app.schemas.user import AdminUserUpdate, UserPublic

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def get_current_user(current_user: CurrentUser) -> User:
    """
    Получение данных текущего авторизованного пользователя
    """
    return current_user


@router.post("/change", response_model=UserPublic)
async def change_user_role(
    session: SessionDep,
    service: UserServiceDep,
    user_in: AdminUserUpdate,
    _: AdminUser,
    email: EmailStr = Query(..., description="Email пользвателя"),
) -> User:
    """
    Изменение роли для конкретного пользователя по email
    """
    user = await service.get_by(session, service.model.email, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = await service.admin_update(session, user, user_in)
    return user

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.models.user import User
from app.schemas.user import UserPublic

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def get_current_user(current_user: CurrentUser) -> User:
    """
    Получение данных текущего авторизованного пользователя
    """
    return current_user

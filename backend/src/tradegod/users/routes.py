from fastapi import APIRouter

from tradegod.auth.dependencies import CurrentUserId
from tradegod.auth.exceptions import InvalidCredentials
from tradegod.core.dependencies import DbSession
from tradegod.users.crud import get_user
from tradegod.users.schemas import UserPublic

users_router = APIRouter(prefix="/users")


@users_router.get("/me")
async def me(db: DbSession, user_id: CurrentUserId) -> UserPublic:
    """Return the currently authenticated user.

    Raises:
        InvalidCredentials (401): missing or invalid access token.
    """
    user = await get_user(db, user_id)
    if not user:
        raise InvalidCredentials
    return UserPublic.model_validate(user)

from fastapi import APIRouter

from tradegod.core.dependencies import DbSession
from tradegod.models.user import User
from tradegod.schemas.user import UserCreate, UserResponse
from tradegod.services.user import register_user

users_router = APIRouter(prefix="/users")


@users_router.post("/register", response_model=UserResponse, status_code=201)
async def register(db: DbSession, payload: UserCreate) -> User:
    user = await register_user(db, username=payload.username, email=payload.email, raw_password=payload.password.get_secret_value())
    await db.commit()
    return user

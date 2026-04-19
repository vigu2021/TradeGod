from fastapi import APIRouter

from tradegod.core.dependencies import DbSession
from tradegod.models.user import User
from tradegod.schemas.user import UserCreate, UserResponse
from tradegod.services.user import register_user

users_router = APIRouter(prefix="/users")


@users_router.post("/register", response_model=UserResponse, status_code=201)
async def register(db: DbSession, payload: UserCreate) -> User:
    """Register a new user account.

    Creates a user with the given username, email, and password. The password
    is hashed with argon2 before being stored.

    Raises:
        AlreadyExists (409): if the username or email is already taken.
        RequestValidationError (422): on schema validation failure
            (length, format, or missing fields).
    """
    user = await register_user(
        db,
        username=payload.username,
        email=payload.email,
        raw_password=payload.password.get_secret_value(),
    )
    return user

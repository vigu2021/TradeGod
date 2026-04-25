from fastapi import APIRouter

from tradegod.core.dependencies import DbSession
from tradegod.models.user import User
from tradegod.schemas.auth import RegisterRequest, RegisterResponse
from tradegod.services.auth import register_user

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(db: DbSession, payload: RegisterRequest) -> User:
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

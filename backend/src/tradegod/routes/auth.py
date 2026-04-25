from typing import Annotated, Final

from fastapi import APIRouter, Cookie, Response

from tradegod.core.dependencies import DbSession
from tradegod.core.exceptions import InvalidCredentials
from tradegod.core.settings import get_settings
from tradegod.schemas.auth import AccessToken, AuthResponse, LoginRequest, RegisterRequest
from tradegod.schemas.user import UserPublic
from tradegod.services.auth import login_account, refresh_account, register_account

auth_router = APIRouter(prefix="/auth")


REFRESH_COOKIE_NAME: Final[str] = "refresh_token"


def set_refresh_cookie(response: Response, raw_refresh_token: str) -> None:
    """Attach the refresh token as an HttpOnly cookie scoped to /auth."""
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_refresh_token,
        max_age=get_settings().refresh_token_expire_days * 86400,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/auth",
    )


@auth_router.post("/register", status_code=201)
async def register(
    db: DbSession,
    payload: RegisterRequest,
    response: Response,
) -> AuthResponse:
    """Register a new user account, set the refresh-token cookie, and return the access token.

    Raises:
        AlreadyExists (409): if the username or email is already taken.
        RequestValidationError (422): on schema validation failure
            (length, format, or missing fields).
    """
    result = await register_account(
        db,
        username=payload.username,
        email=payload.email,
        raw_password=payload.password.get_secret_value(),
    )
    set_refresh_cookie(response, result.tokens.refresh_token)
    return AuthResponse(
        user=UserPublic.model_validate(result.user),
        tokens=AccessToken(access_token=result.tokens.access_token),
    )


@auth_router.post("/login")
async def login(db: DbSession, payload: LoginRequest, response: Response) -> AuthResponse:
    result = await login_account(db, email=payload.email, raw_password=payload.password.get_secret_value())
    set_refresh_cookie(response, result.tokens.refresh_token)
    return AuthResponse(
        user=UserPublic.model_validate(result.user),
        tokens=AccessToken(access_token=result.tokens.access_token),
    )


@auth_router.post("/refresh")
async def refresh(
    db: DbSession,
    response: Response,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)] = None,
) -> AuthResponse:
    """Validate the refresh-token cookie, rotate it, and return a new access token.

    Raises:
        InvalidCredentials (401): cookie missing, or token unknown, revoked, or expired.
    """
    if not refresh_token:
        raise InvalidCredentials
    result = await refresh_account(db, raw_refresh_token=refresh_token)
    set_refresh_cookie(response, result.tokens.refresh_token)
    return AuthResponse(
        user=UserPublic.model_validate(result.user),
        tokens=AccessToken(access_token=result.tokens.access_token),
    )

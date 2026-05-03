from typing import Annotated, Final

from fastapi import APIRouter, Cookie, Response

from tradegod.auth.exceptions import InvalidCredentials
from tradegod.auth.schemas import AccessToken, AuthResponse, LoginRequest, RegisterRequest
from tradegod.auth.services import login_account, logout_account, refresh_account, register_account
from tradegod.core.dependencies import DbSession
from tradegod.core.settings import Environment, get_settings
from tradegod.users.schemas import UserPublic

auth_router = APIRouter(prefix="/auth")


REFRESH_COOKIE_NAME: Final[str] = "refresh_token"


def set_refresh_cookie(response: Response, raw_refresh_token: str) -> None:
    """Attach the refresh token as an HttpOnly cookie."""
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_refresh_token,
        max_age=get_settings().refresh_token_expire_days * 86400,
        httponly=True,
        secure=get_settings().environment != Environment.DEV,
        samesite="lax",
        path="/",
    )


def delete_refresh_cookie(response: Response) -> None:
    """Clear the refresh-token cookie. Attributes must mirror set_refresh_cookie so the browser matches and removes it."""
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        httponly=True,
        secure=get_settings().environment != Environment.DEV,
        samesite="lax",
        path="/",
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
    """Authenticate by email + password, set the refresh-token cookie, and return the access token.

    Raises:
        InvalidCredentials (401): email not found or password mismatch.
        RequestValidationError (422): on schema validation failure
            (invalid email format, missing fields).
    """
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


@auth_router.post("/logout", status_code=204)
async def logout(
    db: DbSession,
    response: Response,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)] = None,
) -> None:
    """Revoke the refresh-token cookie's session and clear it from the browser.

    Idempotent: always returns 204, whether the cookie was present, missing,
    pointed at an unknown token, or already revoked. The access token is not
    revoked (JWTs are stateless) and remains valid until its exp claim, so
    clients should also drop their in-memory copy on logout.
    """
    if refresh_token:
        await logout_account(db, refresh_token)
    delete_refresh_cookie(response)

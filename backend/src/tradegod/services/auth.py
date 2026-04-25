from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.core.exceptions import InvalidCredentials
from tradegod.core.security import (
    generate_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from tradegod.core.settings import get_settings
from tradegod.crud.refresh_token import create_refresh_token
from tradegod.crud.user import create_user, get_user_by_email
from tradegod.models import User


@dataclass(frozen=True, slots=True)
class IssuedTokens:
    access_token: str
    refresh_token: str


@dataclass(frozen=True, slots=True)
class RegisterResult:
    user: User
    tokens: IssuedTokens


@dataclass(frozen=True, slots=True)
class LoginResult:
    user: User
    tokens: IssuedTokens


async def register_account(db: AsyncSession, username: str, email: str, raw_password: str) -> RegisterResult:
    """Register a new user and issue an initial token pair.

    Raises:
        AlreadyExists: if the username or email is already taken.
    """
    hashed_password = await hash_password(raw_password)
    user = await create_user(db, username, email, hashed_password)
    tokens = await _issue_tokens(db, user.id)
    return RegisterResult(user=user, tokens=tokens)


async def login_account(db: AsyncSession, email: str, raw_password: str) -> LoginResult:
    """Authenticate by email + password and issue a token pair.

    Raises:
        InvalidCredentials: email not found or password mismatch.
    """
    user = await get_user_by_email(db, email)

    if not user or not await verify_password(raw_password, user.hashed_password):
        raise InvalidCredentials

    tokens = await _issue_tokens(db, user.id)
    return LoginResult(user=user, tokens=tokens)


async def _issue_tokens(db: AsyncSession, user_id: int) -> IssuedTokens:
    """Mint an access token and persist a new refresh token row."""
    access_token = generate_access_token(user_id)
    raw_refresh_token = generate_refresh_token()
    expires_at = datetime.now(UTC) + timedelta(days=get_settings().refresh_token_expire_days)

    _ = await create_refresh_token(
        db,
        user_id=user_id,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=expires_at,
    )

    return IssuedTokens(
        access_token=access_token,
        refresh_token=raw_refresh_token,
    )

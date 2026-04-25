from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.core.security import (
    generate_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
)
from tradegod.core.settings import get_settings
from tradegod.crud.refresh_token import create_refresh_token
from tradegod.crud.user import create_user
from tradegod.models import User


@dataclass(frozen=True)
class IssuedTokens:
    access_token: str
    refresh_token: str  # raw value — goes into HttpOnly cookie


@dataclass(frozen=True)
class RegisterResult:
    user: User
    tokens: IssuedTokens


async def _issue_tokens(db: AsyncSession, user_id: int) -> IssuedTokens:
    """Mint an access token and persist a new refresh token row."""
    raw_refresh_token = generate_refresh_token()
    expires_at = datetime.now(UTC) + timedelta(days=get_settings().refresh_token_expire_days)

    _ = await create_refresh_token(
        db,
        user_id=user_id,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=expires_at,
    )

    return IssuedTokens(
        access_token=generate_access_token(user_id),
        refresh_token=raw_refresh_token,
    )


async def register_account(db: AsyncSession, username: str, email: str, raw_password: str) -> RegisterResult:
    """Register a new user and issue an initial token pair.

    Raises:
        AlreadyExists: if the username or email is already taken.
    """
    hashed_password = await hash_password(raw_password)
    user = await create_user(db, username, email, hashed_password)
    tokens = await _issue_tokens(db, user.id)
    return RegisterResult(user=user, tokens=tokens)

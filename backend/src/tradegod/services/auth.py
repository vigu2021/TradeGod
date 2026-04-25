from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.stdlib import BoundLogger

from tradegod.core.exceptions import InvalidCredentials
from tradegod.core.security import (
    generate_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from tradegod.core.settings import get_settings
from tradegod.crud.refresh_token import create_refresh_token, get_refresh_token_with_user_by_token_hash
from tradegod.crud.user import create_user, get_user_by_email
from tradegod.models import User

logger: BoundLogger = structlog.get_logger(__name__)


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


@dataclass(frozen=True, slots=True)
class RefreshResult:
    user: User
    tokens: IssuedTokens


async def register_account(db: AsyncSession, username: str, email: str, raw_password: str) -> RegisterResult:
    """Register a new user and issue an initial token pair.

    The password is hashed with argon2 before being persisted. On success the
    caller receives the new user along with a fresh access + refresh token pair.

    Raises:
        AlreadyExists: username or email is already taken.
    """
    hashed_password = await hash_password(raw_password)
    user = await create_user(db, username, email, hashed_password)
    tokens = await _issue_tokens(db, user.id)
    logger.info("auth.register.success", user_id=user.id, username=user.username)
    return RegisterResult(user=user, tokens=tokens)


async def login_account(db: AsyncSession, email: str, raw_password: str) -> LoginResult:
    """Authenticate by email + password and issue a token pair.

    A single error is raised whether the email is unknown or the password
    is wrong, so callers cannot distinguish the two failure modes (avoids
    account-enumeration leaks).

    Raises:
        InvalidCredentials: email not found or password mismatch.
    """
    user = await get_user_by_email(db, email)

    if not user or not await verify_password(raw_password, user.hashed_password):
        raise InvalidCredentials

    tokens = await _issue_tokens(db, user.id)
    logger.info("auth.login.success", user_id=user.id)
    return LoginResult(user=user, tokens=tokens)


async def refresh_account(db: AsyncSession, raw_refresh_token: str) -> RefreshResult:
    """Validate a refresh token and issue a new token pair.

    The supplied token is looked up by its sha256 hash. A single error is
    raised whether the row is missing, revoked, or expired, so callers
    cannot probe to discover which condition failed.

    Raises:
        InvalidCredentials: token not found, revoked, or expired.
    """
    hashed_refresh_token = hash_refresh_token(raw_refresh_token)
    refresh_token = await get_refresh_token_with_user_by_token_hash(db, hashed_refresh_token)
    now = datetime.now(UTC)

    if not refresh_token:
        logger.debug("auth.refresh.failed", reason="unknown_token")
        raise InvalidCredentials
    if refresh_token.expires_at < now:
        logger.debug("auth.refresh.failed", reason="expired", user_id=refresh_token.user_id)
        raise InvalidCredentials
    # Reuse of a revoked token is a strong signal the cookie was stolen.
    if refresh_token.revoked_at is not None:
        logger.warning(
            "auth.refresh.revoked_reuse",
            user_id=refresh_token.user_id,
            token_id=refresh_token.id,
        )
        raise InvalidCredentials

    # Each refresh token works only once. If we see this one again, that's a sign it was stolen.
    refresh_token.revoked_at = now

    tokens = await _issue_tokens(db, refresh_token.user_id)
    logger.info("auth.refresh.success", user_id=refresh_token.user_id)
    return RefreshResult(user=refresh_token.user, tokens=tokens)


async def _issue_tokens(db: AsyncSession, user_id: int) -> IssuedTokens:
    """Mint an access token and persist a new refresh token row.

    The access token is a signed JWT (returned to the client). The refresh
    token is a random opaque string; only its sha256 hash is persisted, so a
    DB leak does not expose usable tokens. The raw refresh token is returned
    so callers can deliver it to the client (typically via HttpOnly cookie).
    """
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

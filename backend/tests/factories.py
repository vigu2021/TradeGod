"""Async factories for building domain objects in tests.

Each factory persists via `session.flush()` (not commit) so the outer
SAVEPOINT-based test transaction stays intact and can be rolled back.
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.auth.models import RefreshToken
from tradegod.auth.security import (
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
)
from tradegod.ledger.models.account import Account, AccountType
from tradegod.users.models import User


def _short_id() -> str:
    return uuid.uuid4().hex[:8]


async def build_user(
    session: AsyncSession,
    *,
    username: str | None = None,
    email: str | None = None,
    password: str = "testpass123",
) -> User:
    """Persist a User with real argon2-hashed password.

    Args:
        session: Active async session inside the test transaction.
        username: Override username, else random unique value.
        email: Override email, else random unique value.
        password: Plaintext password to hash via real argon2.

    Returns:
        The flushed User with id populated.
    """
    suffix = _short_id()
    user = User(
        username=username or f"user_{suffix}",
        email=email or f"user_{suffix}@example.com",
        hashed_password=await hash_password(password),
    )
    session.add(user)
    # flush not commit: keeps the SAVEPOINT chain alive for rollback
    await session.flush()
    return user


async def build_account(
    session: AsyncSession,
    user_id: int,
    *,
    name: str | None = None,
    account_type: AccountType = AccountType.CASH,
    provider: str | None = "test",
) -> Account:
    """Persist an Account for the given user.

    Args:
        session: Active async session inside the test transaction.
        user_id: Owning user id.
        name: Override account name, else random unique value.
        account_type: AccountType enum value.
        provider: Optional provider string.

    Returns:
        The flushed Account with id populated.
    """
    account = Account(
        user_id=user_id,
        name=name or f"account_{_short_id()}",
        account_type=account_type,
        provider=provider,
    )
    session.add(account)
    await session.flush()
    return account


async def build_refresh_token(
    session: AsyncSession,
    user_id: int,
    *,
    expired: bool = False,
    revoked: bool = False,
) -> tuple[RefreshToken, str]:
    """Persist a RefreshToken row in the requested state.

    Args:
        session: Active async session inside the test transaction.
        user_id: Owning user id.
        expired: If True, expires_at is set in the past.
        revoked: If True, revoked_at is set in the past.

    Returns:
        Tuple of the flushed RefreshToken row and the plaintext token string
        (only the hash is persisted; plaintext is needed by callers that
        simulate the refresh flow over HTTP).
    """
    now = datetime.now(UTC)
    expires_at = now - timedelta(days=1) if expired else now + timedelta(days=7)
    revoked_at = now - timedelta(hours=1) if revoked else None

    plaintext = generate_refresh_token()
    token = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(plaintext),
        expires_at=expires_at,
        revoked_at=revoked_at,
    )
    session.add(token)
    await session.flush()
    return token, plaintext

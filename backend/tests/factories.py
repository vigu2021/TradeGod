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
from tradegod.ledger.models.asset import Asset, AssetType
from tradegod.users.models import User


def _short_id() -> str:
    return uuid.uuid4().hex[:12]


async def build_user(
    session: AsyncSession,
    *,
    username: str | None = None,
    email: str | None = None,
    password: str = "testpass123",
) -> User:
    # real argon2: no monkeypatching
    suffix = _short_id()
    user = User(
        username=username or f"user_{suffix}",
        email=email or f"user_{suffix}@example.com",
        hashed_password=await hash_password(password),
    )
    session.add(user)
    # flush not commit: keeps SAVEPOINT chain alive for rollback
    await session.flush()
    return user


async def build_account(
    session: AsyncSession,
    user_id: int,
    *,
    name: str | None = None,
    account_type: AccountType = AccountType.CASH,
    provider: str | None = None,
) -> Account:
    account = Account(
        user_id=user_id,
        name=name or f"account_{_short_id()}",
        account_type=account_type,
        provider=provider,
    )
    session.add(account)
    await session.flush()
    return account


async def build_asset(
    session: AsyncSession,
    *,
    symbol: str | None = None,
    name: str | None = None,
    asset_type: AssetType = AssetType.STOCK,
) -> Asset:
    suffix = _short_id()
    asset = Asset(
        asset_type=asset_type,
        symbol=symbol or f"SYM_{suffix}".upper()[:20],
        name=name or f"asset_{suffix}",
    )
    session.add(asset)
    await session.flush()
    return asset


async def build_refresh_token(
    session: AsyncSession,
    user_id: int,
    *,
    expired: bool = False,
    revoked: bool = False,
) -> tuple[RefreshToken, str]:
    # returns (row, plaintext) so callers can simulate the http refresh flow
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

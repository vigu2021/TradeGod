from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from tradegod.models import RefreshToken


async def create_refresh_token(
    db: AsyncSession,
    *,
    user_id: int,
    token_hash: str,
    expires_at: datetime,
) -> RefreshToken:
    refresh_token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(refresh_token)
    await db.flush()
    return refresh_token


async def get_refresh_token_with_user_by_token_hash(db: AsyncSession, token_hash: str) -> RefreshToken | None:
    stmt = select(RefreshToken).options(joinedload(RefreshToken.user)).where(RefreshToken.token_hash == token_hash)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

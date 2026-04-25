from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

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

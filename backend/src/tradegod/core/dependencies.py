from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from tradegod.core.database import async_session
from tradegod.core.security import decode_access_token


# Get a db session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Validate auth token and get the user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_id(access_token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    payload = decode_access_token(access_token)
    return int(payload["sub"])


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
DbSession = Annotated[AsyncSession, Depends(get_db, scope="function")]

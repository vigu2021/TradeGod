from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .settings import get_settings

engine = create_async_engine(get_settings().database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# All SQLAlchemy models inherit from this to share metadata and table registry
class Base(DeclarativeBase):
    pass


# FastAPI dependency — use with Depends(get_db)
async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session

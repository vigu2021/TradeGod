from enum import Enum
from typing import ClassVar, Final

from sqlalchemy import Enum as SAEnum
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .settings import get_settings


def sql_enum(enum_cls: type[Enum], name: str, length: int = 16) -> SAEnum:
    # stores .value not .name, varchar + check constraint
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=False,
        length=length,
        create_constraint=True,
        values_callable=lambda cls: [e.value for e in cls],  # pyright: ignore[reportUnknownLambdaType]
    )


NAMING_CONVENTION: Final[dict[str, str]] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

engine: Final[AsyncEngine] = create_async_engine(get_settings().database_url, pool_pre_ping=True)
async_session: Final[async_sessionmaker[AsyncSession]] = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    metadata: ClassVar[MetaData] = MetaData(naming_convention=NAMING_CONVENTION)

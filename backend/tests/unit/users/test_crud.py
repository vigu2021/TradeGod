import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.auth.security import hash_password
from tradegod.core.exceptions import AlreadyExists
from tradegod.users.crud import create_user, get_user, get_user_by_email
from tradegod.users.models import User

pytestmark = pytest.mark.asyncio


async def test_get_user_found(db_session: AsyncSession, user: User) -> None:
    found = await get_user(db_session, user.id)
    assert found is not None
    assert found.id == user.id


async def test_get_user_missing(db_session: AsyncSession) -> None:
    assert await get_user(db_session, 999_999_999) is None


async def test_get_user_by_email_found(db_session: AsyncSession, user: User) -> None:
    found = await get_user_by_email(db_session, user.email)
    assert found is not None
    assert found.id == user.id


async def test_get_user_by_email_missing(db_session: AsyncSession) -> None:
    assert await get_user_by_email(db_session, "nope_missing@example.com") is None


async def test_create_user_happy(db_session: AsyncSession) -> None:
    created = await create_user(
        db_session,
        username="fresh_user",
        email="fresh_user@example.com",
        hashed_password=await hash_password("anypassword"),
    )
    assert created.id is not None
    assert created.username == "fresh_user"
    assert created.email == "fresh_user@example.com"


async def test_create_user_duplicate_username(db_session: AsyncSession, user: User) -> None:
    with pytest.raises(AlreadyExists):
        _ = await create_user(
            db_session,
            username=user.username,
            email="different_email@example.com",
            hashed_password=await hash_password("anypassword"),
        )


async def test_create_user_duplicate_email(db_session: AsyncSession, user: User) -> None:
    with pytest.raises(AlreadyExists):
        _ = await create_user(
            db_session,
            username="different_username",
            email=user.email,
            hashed_password=await hash_password("anypassword"),
        )

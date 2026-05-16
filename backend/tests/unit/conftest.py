import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.ledger.models.account import Account
from tradegod.users.models import User
from tests.factories import build_account, build_user


@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    return await build_user(db_session)


@pytest_asyncio.fixture
async def account(db_session: AsyncSession, user: User) -> Account:
    return await build_account(db_session, user.id)

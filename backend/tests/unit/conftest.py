import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.ledger.models.account import Account
from tradegod.ledger.models.asset import Asset, AssetType
from tradegod.users.models import User
from tests.factories import build_account, build_asset, build_user


@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    return await build_user(db_session)


@pytest_asyncio.fixture
async def account(db_session: AsyncSession, user: User) -> Account:
    return await build_account(db_session, user.id)


@pytest_asyncio.fixture
async def usd_asset(db_session: AsyncSession) -> Asset:
    return await build_asset(db_session, symbol="USD", name="US Dollar", asset_type=AssetType.FIAT)


@pytest_asyncio.fixture
async def aapl_asset(db_session: AsyncSession) -> Asset:
    return await build_asset(db_session, symbol="AAPL", name="Apple Inc", asset_type=AssetType.STOCK)

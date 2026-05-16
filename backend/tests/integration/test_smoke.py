import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import build_user
from tradegod.users.models import User

pytestmark = pytest.mark.asyncio


async def test_root_returns_200(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "TradeGod API"}


async def test_db_session_isolation_create(db_session: AsyncSession) -> None:
    # creates a user; the next test must not see it
    user = await build_user(db_session)
    assert user.id is not None


async def test_db_session_isolation_verify(db_session: AsyncSession) -> None:
    result = await db_session.execute(select(User))
    assert result.scalars().all() == [], "previous test's user leaked across rollback boundary"

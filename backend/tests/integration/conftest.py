from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.auth.dependencies import get_current_user_id
from tradegod.core.dependencies import get_db
from tradegod.main import app
from tradegod.users.models import User
from tests.factories import build_user


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        # no commit, the outer transaction owns the lifecycle
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as http_client:
            yield http_client
    finally:
        _ = app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def authed_client(
    client: AsyncClient,
    db_session: AsyncSession,
) -> AsyncGenerator[tuple[AsyncClient, User], None]:
    user = await build_user(db_session)

    def override_user_id() -> int:
        return user.id

    app.dependency_overrides[get_current_user_id] = override_user_id
    try:
        yield client, user
    finally:
        _ = app.dependency_overrides.pop(get_current_user_id, None)

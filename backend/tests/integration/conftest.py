import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import Session as SyncSession
from sqlalchemy.orm import SessionTransaction

from tradegod.auth.dependencies import get_current_user_id
from tradegod.core.dependencies import get_db
from tradegod.main import app
from tradegod.users.models import User
from tests.factories import build_user


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(os.environ["TEST_DATABASE_URL"], pool_pre_ping=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def _migrated_db() -> None:
    # alembic runs sync, strip the asyncpg driver tag
    config = Config("alembic.ini")
    config.set_main_option(
        "sqlalchemy.url",
        os.environ["TEST_DATABASE_URL"].replace("+asyncpg", ""),
    )
    command.upgrade(config, "head")


# referenced so basedpyright sees the autouse fixture as used
_migrated_db_fixture = _migrated_db


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )

        # restart SAVEPOINT after app code commits so each test stays isolated
        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(sync_session: SyncSession, transaction_state: SessionTransaction) -> None:
            parent = transaction_state.parent
            if transaction_state.nested and parent is not None and not parent.nested:
                _ = sync_session.begin_nested()

        # listener registration is the side effect; bind to silence unused-function
        _restart_savepoint_ref = restart_savepoint

        try:
            yield session
        finally:
            del _restart_savepoint_ref
            await session.close()
            await transaction.rollback()


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
    app.dependency_overrides[get_current_user_id] = lambda: user.id
    try:
        yield client, user
    finally:
        _ = app.dependency_overrides.pop(get_current_user_id, None)

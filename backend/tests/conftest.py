"""Test session bootstrap: load .env.test, validate, then provide shared engine
and savepoint-based db_session fixtures used by both unit and integration tests.

Env loading runs BEFORE any tradegod import to guarantee get_settings()'s
lru_cache is never primed against process env before .env.test overrides it.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from dotenv import load_dotenv

_ = load_dotenv(Path(__file__).resolve().parent.parent / ".env.test", override=False)

if not os.environ.get("TEST_DATABASE_URL"):
    pytest.exit("TEST_DATABASE_URL is not set; cannot run tests.", returncode=2)

# import after env load so the cache primes against test env, not process env
import pytest_asyncio  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from argon2 import PasswordHasher  # noqa: E402
from sqlalchemy import event  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine  # noqa: E402
from sqlalchemy.orm import Session as SyncSession  # noqa: E402
from sqlalchemy.orm import SessionTransaction  # noqa: E402

from tradegod.auth import security as _security  # noqa: E402
from tradegod.core.settings import get_settings  # noqa: E402

get_settings.cache_clear()

# swap argon2 to cheap params for the whole test session so the suite stays fast.
# kept here (not in src) so prod argon2 cost is never accidentally weakened.
# _ph is Final, but we deliberately reassign at runtime so reads in hash_password/
# verify_password pick up the cheap instance.
_security._ph = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)  # pyright: ignore[reportPrivateUsage]


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

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()

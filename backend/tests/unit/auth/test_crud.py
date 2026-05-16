from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.auth.crud import (
    create_refresh_token,
    get_refresh_token_by_token_hash,
    get_refresh_token_with_user_by_token_hash,
)
from tradegod.auth.models import RefreshToken
from tradegod.auth.security import generate_refresh_token, hash_refresh_token
from tradegod.users.models import User
from tests.factories import build_refresh_token

pytestmark = pytest.mark.asyncio


async def test_create_refresh_token_returns_row_with_fields(db_session: AsyncSession, user: User) -> None:
    plaintext = generate_refresh_token()
    token_hash = hash_refresh_token(plaintext)
    expires_at = datetime.now(UTC) + timedelta(days=7)

    token = await create_refresh_token(db_session, user_id=user.id, token_hash=token_hash, expires_at=expires_at)

    assert token.id is not None
    assert token.user_id == user.id
    assert token.token_hash == token_hash
    assert token.expires_at == expires_at


async def test_create_refresh_token_is_queryable_after_flush(db_session: AsyncSession, user: User) -> None:
    plaintext = generate_refresh_token()
    token_hash = hash_refresh_token(plaintext)
    expires_at = datetime.now(UTC) + timedelta(days=7)

    created = await create_refresh_token(db_session, user_id=user.id, token_hash=token_hash, expires_at=expires_at)

    fetched = await db_session.scalar(select(RefreshToken).where(RefreshToken.id == created.id))
    assert fetched is not None
    assert fetched.token_hash == token_hash


async def test_get_refresh_token_by_token_hash_found(db_session: AsyncSession, user: User) -> None:
    token, _plaintext = await build_refresh_token(db_session, user.id)

    fetched = await get_refresh_token_by_token_hash(db_session, token.token_hash)

    assert fetched is not None
    assert fetched.id == token.id


async def test_get_refresh_token_by_token_hash_missing(db_session: AsyncSession) -> None:
    fetched = await get_refresh_token_by_token_hash(db_session, "nonexistent-hash")
    assert fetched is None


async def test_get_refresh_token_with_user_by_token_hash_found(db_session: AsyncSession, user: User) -> None:
    token, _plaintext = await build_refresh_token(db_session, user.id)

    # clear identity map so the get must rely on joinedload, not cached user
    db_session.expunge_all()

    fetched = await get_refresh_token_with_user_by_token_hash(db_session, token.token_hash)

    assert fetched is not None
    # user must be loaded eagerly into __dict__ by joinedload before any attribute access;
    # if joinedload were removed, the lazy="raise" relationship would raise on .user access
    assert "user" in fetched.__dict__
    assert fetched.user.id == user.id


async def test_get_refresh_token_with_user_by_token_hash_missing(
    db_session: AsyncSession,
) -> None:
    fetched = await get_refresh_token_with_user_by_token_hash(db_session, "nonexistent-hash")
    assert fetched is None

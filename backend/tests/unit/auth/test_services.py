import pytest
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.auth.exceptions import InvalidCredentials
from tradegod.auth.models import RefreshToken
from tradegod.auth.services import (
    login_account,
    logout_account,
    refresh_account,
    register_account,
)
from tradegod.core.exceptions import AlreadyExists
from tradegod.users.models import User
from tests.factories import build_refresh_token, build_user

pytestmark = pytest.mark.asyncio


# ---------- register_account ----------


async def test_register_creates_user_and_issues_tokens(db_session: AsyncSession) -> None:
    result = await register_account(db_session, "alice", "alice@example.com", "s3cret-pw")

    assert result.user.username == "alice"
    assert result.user.email == "alice@example.com"
    assert result.tokens.access_token
    assert result.tokens.refresh_token


async def test_register_hashes_password(db_session: AsyncSession) -> None:
    raw_password = "s3cret-pw"
    result = await register_account(db_session, "bob", "bob@example.com", raw_password)

    stored = await db_session.get(User, result.user.id)
    assert stored is not None
    assert stored.hashed_password != raw_password
    assert stored.hashed_password.startswith("$argon2")


async def test_register_duplicate_username_raises(db_session: AsyncSession) -> None:
    _ = await register_account(db_session, "carol", "carol@example.com", "pw1234567")

    with pytest.raises(AlreadyExists):
        _ = await register_account(db_session, "carol", "other@example.com", "pw1234567")


async def test_register_duplicate_email_raises(db_session: AsyncSession) -> None:
    _ = await register_account(db_session, "dave", "dup@example.com", "pw1234567")

    with pytest.raises(AlreadyExists):
        _ = await register_account(db_session, "other", "dup@example.com", "pw1234567")


# ---------- login_account ----------


async def test_login_success(db_session: AsyncSession) -> None:
    user = await build_user(db_session, email="login@example.com", password="testpass123")

    result = await login_account(db_session, "login@example.com", "testpass123")

    assert result.user.id == user.id
    assert result.tokens.access_token
    assert result.tokens.refresh_token


async def test_login_unknown_email_raises(db_session: AsyncSession) -> None:
    with pytest.raises(InvalidCredentials):
        _ = await login_account(db_session, "nobody@example.com", "whatever")


async def test_login_wrong_password_raises(db_session: AsyncSession, user: User) -> None:
    with pytest.raises(InvalidCredentials):
        _ = await login_account(db_session, user.email, "wrong-password")


# ---------- refresh_account ----------


async def test_refresh_success_revokes_old_token(db_session: AsyncSession, user: User) -> None:
    token_row, plaintext = await build_refresh_token(db_session, user.id)

    result = await refresh_account(db_session, plaintext)

    assert result.user.id == user.id
    assert result.tokens.access_token
    assert result.tokens.refresh_token

    await db_session.refresh(token_row)
    assert token_row.revoked_at is not None


async def test_refresh_unknown_token_raises(db_session: AsyncSession) -> None:
    with pytest.raises(InvalidCredentials):
        _ = await refresh_account(db_session, "this-token-does-not-exist")


async def test_refresh_expired_token_raises(db_session: AsyncSession, user: User) -> None:
    _, plaintext = await build_refresh_token(db_session, user.id, expired=True)

    with pytest.raises(InvalidCredentials):
        _ = await refresh_account(db_session, plaintext)


async def test_refresh_revoked_token_reuse_logs_warning(db_session: AsyncSession, user: User) -> None:
    token_row, plaintext = await build_refresh_token(db_session, user.id, revoked=True)

    with structlog.testing.capture_logs() as cap_logs:
        with pytest.raises(InvalidCredentials):
            _ = await refresh_account(db_session, plaintext)

    matches = [e for e in cap_logs if e.get("event") == "auth.refresh.revoked_reuse"]
    assert len(matches) == 1, "exactly one revoked-reuse log expected"
    entry = matches[0]
    # security-critical: must be at warning level so it reaches alerting
    assert entry["log_level"] == "warning"
    assert entry["user_id"] == user.id
    assert entry["token_id"] == token_row.id


# ---------- logout_account ----------


async def test_logout_revokes_active_token(db_session: AsyncSession, user: User) -> None:
    token_row, plaintext = await build_refresh_token(db_session, user.id)
    assert token_row.revoked_at is None

    await logout_account(db_session, plaintext)

    # re-query rather than rely on identity-map mutation; survives refactor to UPDATE...WHERE
    fresh = await db_session.scalar(select(RefreshToken).where(RefreshToken.id == token_row.id))
    assert fresh is not None
    assert fresh.revoked_at is not None


async def test_logout_unknown_token_is_noop(db_session: AsyncSession) -> None:
    # should not raise
    await logout_account(db_session, "totally-unknown-token")


async def test_logout_already_revoked_token_is_noop(db_session: AsyncSession, user: User) -> None:
    token_row, plaintext = await build_refresh_token(db_session, user.id, revoked=True)
    original_revoked_at = token_row.revoked_at

    await logout_account(db_session, plaintext)

    # confirm timestamp unchanged: re-query via select to avoid stale identity-map state
    fresh = await db_session.scalar(select(RefreshToken).where(RefreshToken.id == token_row.id))
    assert fresh is not None
    assert fresh.revoked_at == original_revoked_at

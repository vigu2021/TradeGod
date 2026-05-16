import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.core.exceptions import AlreadyExists, NotFoundError
from tradegod.ledger.crud.account import archive_account, create_account, get_all_accounts
from tradegod.ledger.models.account import Account, AccountType
from tradegod.users.models import User
from tests.factories import build_account, build_user

pytestmark = pytest.mark.asyncio


async def test_create_account_happy(db_session: AsyncSession, user: User) -> None:
    account = await create_account(
        db_session,
        user_id=user.id,
        account_type=AccountType.CASH,
        name="checking",
        provider=None,
    )
    assert account.id is not None
    assert account.user_id == user.id
    assert account.name == "checking"
    assert account.account_type == AccountType.CASH
    assert account.is_archived is False


async def test_create_account_duplicate_name_same_user_raises(db_session: AsyncSession, user: User) -> None:
    _ = await create_account(
        db_session,
        user_id=user.id,
        account_type=AccountType.CASH,
        name="dup",
        provider=None,
    )
    with pytest.raises(AlreadyExists):
        _ = await create_account(
            db_session,
            user_id=user.id,
            account_type=AccountType.BANK,
            name="dup",
            provider=None,
        )


async def test_create_account_same_name_different_user_allowed(db_session: AsyncSession, user: User) -> None:
    _ = await create_account(
        db_session,
        user_id=user.id,
        account_type=AccountType.CASH,
        name="shared",
        provider=None,
    )
    second = await build_user(db_session, username="other", email="other@example.com")
    account = await create_account(
        db_session,
        user_id=second.id,
        account_type=AccountType.CASH,
        name="shared",
        provider=None,
    )
    assert account.user_id == second.id
    assert account.name == "shared"


async def test_get_all_accounts_excludes_archived(db_session: AsyncSession, user: User, account: Account) -> None:
    archived = await build_account(db_session, user.id, name="archived_one")
    archived.is_archived = True
    await db_session.flush()

    results = await get_all_accounts(db_session, user.id)
    ids = {row.id for row in results}
    assert account.id in ids
    assert archived.id not in ids


async def test_get_all_accounts_empty_for_new_user(db_session: AsyncSession) -> None:
    fresh = await build_user(db_session, username="fresh", email="fresh@example.com")
    assert await get_all_accounts(db_session, fresh.id) == []


async def test_get_all_accounts_scoped_to_owner(db_session: AsyncSession, user: User, account: Account) -> None:
    second = await build_user(db_session, username="other2", email="other2@example.com")
    _ = await build_account(db_session, second.id, name="not_yours")

    results = await get_all_accounts(db_session, user.id)
    assert [row.id for row in results] == [account.id]


async def test_archive_account_happy(db_session: AsyncSession, user: User, account: Account) -> None:
    await archive_account(db_session, user.id, account.id)
    await db_session.refresh(account)
    assert account.is_archived is True


async def test_archive_account_missing_raises(db_session: AsyncSession, user: User) -> None:
    with pytest.raises(NotFoundError):
        await archive_account(db_session, user.id, 999999)


async def test_archive_account_other_user_raises(db_session: AsyncSession, account: Account) -> None:
    second = await build_user(db_session, username="other3", email="other3@example.com")
    with pytest.raises(NotFoundError):
        await archive_account(db_session, second.id, account.id)

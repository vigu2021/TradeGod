from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.core.exceptions import AlreadyExists, NotFoundError
from tradegod.ledger.models import Account, AccountType


async def create_account(db: AsyncSession, user_id: int, account_type: AccountType, name: str, provider: str | None) -> Account:
    """Insert a new account and flush so uniqueness constraints fire immediately.

    Transaction lifecycle (commit/rollback) is owned by the session dependency.

    Raises:
        AlreadyExists: an account with this name already exists for this user.
    """
    account = Account(user_id=user_id, account_type=account_type, name=name, provider=provider)
    db.add(account)
    try:
        await db.flush()
    except IntegrityError as e:
        raise AlreadyExists("An account with this name already exists") from e
    return account


async def get_all_accounts(db: AsyncSession, user_id: int) -> list[Account]:
    stmt = select(Account).where(Account.user_id == user_id, Account.is_archived.is_(False)).order_by(Account.created_at.desc())
    result = await db.scalars(stmt)
    return list(result.all())


async def archive_account(db: AsyncSession, user_id: int, account_id: int) -> None:
    stmt = update(Account).where(Account.id == account_id, Account.user_id == user_id).values(is_archived=True).returning(Account.id)
    if await db.scalar(stmt) is None:
        raise NotFoundError("Account not found, failed to archive!")

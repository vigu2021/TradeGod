from fastapi import APIRouter

from tradegod.auth.dependencies import CurrentUserId
from tradegod.core.dependencies import DbSession
from tradegod.ledger.crud import account as account_crud
from tradegod.ledger.schemas.account import AccountCreateRequest, AccountPublic

account_router = APIRouter(prefix="/accounts")


@account_router.get("")
async def list_accounts(db: DbSession, user_id: CurrentUserId) -> list[AccountPublic]:
    """List the current user's non-archived accounts, newest first."""
    accounts = await account_crud.get_all_accounts(db, user_id=user_id)
    return [AccountPublic.model_validate(account) for account in accounts]


@account_router.post("", status_code=201)
async def create_account(
    db: DbSession,
    user_id: CurrentUserId,
    payload: AccountCreateRequest,
) -> AccountPublic:
    """Create a new account for the current user.

    Raises:
        AlreadyExists (409): account with this name already exists for this user.
        RequestValidationError (422): on schema validation failure.
    """
    account = await account_crud.create_account(
        db,
        user_id=user_id,
        account_type=payload.account_type,
        name=payload.name,
        provider=payload.provider,
    )
    return AccountPublic.model_validate(account)


@account_router.post("/{account_id}/archive", status_code=204)
async def archive_account(
    db: DbSession,
    user_id: CurrentUserId,
    account_id: int,
) -> None:
    """Archive an account. Idempotent on already-archived accounts.

    Raises:
        NotFoundError (404): account does not exist or does not belong to this user.
    """
    await account_crud.archive_account(db, user_id=user_id, account_id=account_id)

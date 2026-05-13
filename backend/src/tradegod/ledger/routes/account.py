from fastapi import APIRouter

from tradegod.auth.dependencies import CurrentUserId
from tradegod.core.dependencies import DbSession
from tradegod.ledger.crud.account import get_all_accounts
from tradegod.ledger.schemas.account import AccountPublic

account_router = APIRouter(prefix="/accounts")


@account_router.get("")
async def list_accounts(db: DbSession, user_id: CurrentUserId) -> list[AccountPublic]:
    accounts = await get_all_accounts(db, user_id=user_id)
    return [AccountPublic.model_validate(account) for account in accounts]

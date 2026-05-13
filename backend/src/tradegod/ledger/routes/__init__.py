from fastapi import APIRouter

from tradegod.ledger.routes.account import account_router


ledger_router = APIRouter()
ledger_router.include_router(account_router)

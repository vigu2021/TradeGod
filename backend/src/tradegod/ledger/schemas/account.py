from datetime import datetime

from pydantic import Field

from tradegod.core.schemas import PublicModel
from tradegod.ledger.models import AccountType


class AccountPublic(PublicModel):
    id: int
    account_type: AccountType
    name: str
    provider: str | None
    created_at: datetime
    updated_at: datetime


class AccountCreateRequest(PublicModel):
    account_type: AccountType
    name: str = Field(min_length=1, max_length=100)
    provider: str | None = None

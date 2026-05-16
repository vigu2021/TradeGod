from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

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
    provider: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] | None = None

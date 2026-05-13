from datetime import datetime

from tradegod.core.schemas import PublicModel
from tradegod.ledger.models import AccountType


class AccountPublic(PublicModel):
    id: int
    account_type: AccountType
    name: str
    provider: str | None
    created_at: datetime
    updated_at: datetime

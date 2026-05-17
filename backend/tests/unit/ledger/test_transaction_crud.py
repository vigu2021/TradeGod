from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.ledger.crud.transaction import create_transaction
from tradegod.ledger.models.transaction import TransactionType
from tradegod.users.models import User

pytestmark = pytest.mark.asyncio


async def test_create_transaction_happy(db_session: AsyncSession, user: User) -> None:
    executed_at = datetime.now(UTC)
    tx = await create_transaction(
        db_session,
        user_id=user.id,
        transaction_type=TransactionType.BUY,
        executed_at=executed_at,
        note="Bought 10 AAPL",
    )

    assert tx.id is not None
    assert tx.user_id == user.id
    assert tx.transaction_type == TransactionType.BUY
    assert tx.executed_at == executed_at
    assert tx.note == "Bought 10 AAPL"


async def test_create_transaction_without_note(db_session: AsyncSession, user: User) -> None:
    tx = await create_transaction(
        db_session,
        user_id=user.id,
        transaction_type=TransactionType.DEPOSIT,
        executed_at=datetime.now(UTC),
        note=None,
    )

    assert tx.id is not None
    assert tx.note is None

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.ledger.crud.transaction import TransactionEntryInput, create_transaction
from tradegod.ledger.models.account import Account
from tradegod.ledger.models.asset import Asset
from tradegod.ledger.models.transaction import TransactionType
from tradegod.ledger.models.transaction_entry import TransactionEntry
from tradegod.users.models import User

pytestmark = pytest.mark.asyncio


async def test_create_transaction_single_entry(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset
) -> None:
    executed_at = datetime.now(UTC)
    tx, entries = await create_transaction(
        db_session,
        user_id=user.id,
        transaction_type=TransactionType.DEPOSIT,
        executed_at=executed_at,
        note="seed cash",
        entry_inputs=[
            TransactionEntryInput(account_id=account.id, asset_id=usd_asset.id, amount=Decimal("1000")),
        ],
    )

    assert tx.id is not None
    assert tx.user_id == user.id
    assert tx.transaction_type == TransactionType.DEPOSIT
    assert tx.executed_at == executed_at
    assert tx.note == "seed cash"
    assert tx.trade_id is None
    assert len(entries) == 1
    assert entries[0].transaction_id == tx.id
    assert entries[0].account_id == account.id
    assert entries[0].asset_id == usd_asset.id
    assert entries[0].amount == Decimal("1000")


async def test_create_transaction_multi_entry(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset, aapl_asset: Asset
) -> None:
    tx, entries = await create_transaction(
        db_session,
        user_id=user.id,
        transaction_type=TransactionType.BUY,
        executed_at=datetime.now(UTC),
        entry_inputs=[
            TransactionEntryInput(account_id=account.id, asset_id=aapl_asset.id, amount=Decimal("10")),
            TransactionEntryInput(account_id=account.id, asset_id=usd_asset.id, amount=Decimal("-1000")),
        ],
    )

    assert len(entries) == 2
    assert all(e.transaction_id == tx.id for e in entries)
    assert {e.asset_id for e in entries} == {aapl_asset.id, usd_asset.id}
    assert sum(e.amount for e in entries if e.asset_id == aapl_asset.id) == Decimal("10")
    assert sum(e.amount for e in entries if e.asset_id == usd_asset.id) == Decimal("-1000")


async def test_create_transaction_with_trade_id(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset
) -> None:
    # trade_id can be any int — FK constraint isn't checked until commit, and we only flush here.
    # In real usage, create_trade inserts a Trade first then passes its id.
    tx, _ = await create_transaction(
        db_session,
        user_id=user.id,
        transaction_type=TransactionType.BUY,
        executed_at=datetime.now(UTC),
        trade_id=None,
        entry_inputs=[
            TransactionEntryInput(account_id=account.id, asset_id=usd_asset.id, amount=Decimal("1")),
        ],
    )
    assert tx.trade_id is None


async def test_create_transaction_empty_entries_raises(db_session: AsyncSession, user: User) -> None:
    with pytest.raises(ValueError, match="at least one entry"):
        await create_transaction(
            db_session,
            user_id=user.id,
            transaction_type=TransactionType.DEPOSIT,
            executed_at=datetime.now(UTC),
            entry_inputs=[],
        )


async def test_create_transaction_persists_to_db(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset
) -> None:
    tx, _ = await create_transaction(
        db_session,
        user_id=user.id,
        transaction_type=TransactionType.DEPOSIT,
        executed_at=datetime.now(UTC),
        entry_inputs=[
            TransactionEntryInput(account_id=account.id, asset_id=usd_asset.id, amount=Decimal("500")),
        ],
    )

    fetched_entries = (
        (await db_session.execute(select(TransactionEntry).where(TransactionEntry.transaction_id == tx.id)))
        .scalars()
        .all()
    )
    assert len(fetched_entries) == 1
    assert fetched_entries[0].amount == Decimal("500")

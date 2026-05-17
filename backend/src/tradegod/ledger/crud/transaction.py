from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.ledger.models import Transaction, TransactionEntry
from tradegod.ledger.models.transaction import TransactionType


@dataclass(slots=True, frozen=True)
class TransactionEntryInput:
    account_id: int
    asset_id: int
    amount: Decimal


async def create_transaction(
    db: AsyncSession,
    *,
    user_id: int,
    transaction_type: TransactionType,
    executed_at: datetime,
    note: str | None = None,
    trade_id: int | None = None,
    entry_inputs: list[TransactionEntryInput],
) -> tuple[Transaction, list[TransactionEntry]]:
    """Create a transaction and its entries atomically.

    Args:
        db: Active async session. Caller owns the surrounding commit/rollback.
        user_id: Owner of the transaction.
        transaction_type: Category of the transaction (DEPOSIT, BUY, SELL, ...).
        executed_at: When the transaction actually happened (tz-aware).
        note: Optional free-text note attached to the transaction.
        trade_id: FK to a `trades` row when this transaction is the ledger side
            of a trade; None for non-trade events (deposits, transfers, etc.).
        entry_inputs: One or more entries that make up the transaction. Must be
            non-empty. Sign convention: positive amounts increase the account's
            holding of the asset, negative amounts decrease it.

    Returns:
        Tuple of the persisted Transaction and the list of persisted
        TransactionEntry rows, with primary keys populated.

    Raises:
        ValueError: If `entry_inputs` is empty.
    """
    if not entry_inputs:
        raise ValueError("You must provide at least one entry to create a transaction")

    # 1. Add to transaction table
    transaction = Transaction(
        user_id=user_id, transaction_type=transaction_type, executed_at=executed_at, note=note, trade_id=trade_id
    )
    db.add(transaction)
    await db.flush()

    # 2. Insert entries with the new transaction.id
    entries = [
        TransactionEntry(
            transaction_id=transaction.id,
            account_id=entry.account_id,
            asset_id=entry.asset_id,
            amount=entry.amount,
        )
        for entry in entry_inputs
    ]
    db.add_all(entries)
    await db.flush()
    return transaction, entries

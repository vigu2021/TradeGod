from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.ledger.crud.transaction import TransactionEntryInput, create_transaction
from tradegod.ledger.models.trade import Trade, TradeSide
from tradegod.ledger.models.transaction import TransactionType

ZERO_DECIMAL = Decimal("0")


async def create_trade(
    db: AsyncSession,
    *,
    user_id: int,
    account_id: int,
    base_asset_id: int,
    quote_asset_id: int,
    trade_side: TradeSide,
    quantity: Decimal,
    price_per_unit: Decimal,
    executed_at: datetime,
    fees: Decimal = ZERO_DECIMAL,
    note: str | None = None,
) -> Trade:
    """Create a trade and its balanced ledger entries atomically.

    Writes one `trades` row, one `transactions` row (linked via `trade_id`), and
    two `transaction_entries` rows (base leg + quote leg) in a single DB
    transaction. Fees are assumed to be denominated in the quote asset and are
    folded into the quote leg.

    Args:
        db: Active async session. Caller owns the surrounding commit/rollback.
        user_id: Owner of the trade.
        account_id: Brokerage/wallet account holding both base and quote.
        base_asset_id: Asset being bought or sold (e.g. AAPL, BTC).
        quote_asset_id: Asset used to settle the trade (e.g. USD, USDT, ETH).
            Must differ from `base_asset_id`.
        trade_side: BUY or SELL. Determines entry signs.
        quantity: Unsigned amount of the base asset traded. Must be > 0.
        price_per_unit: Price of one unit of base, in quote terms. Must be > 0.
        executed_at: When the trade actually happened (tz-aware).
        fees: Fee charged, in the quote asset. Must be >= 0.
        note: Optional free-text note attached to the transaction.

    Returns:
        The persisted Trade row with `id` populated.

    Raises:
        ValueError: If `quantity` or `price_per_unit` is not > 0, `fees` is
            negative, or `base_asset_id == quote_asset_id`.
    """
    if quantity <= 0:
        raise ValueError("quantity must be > 0 (direction is determined by trade_side)")
    if price_per_unit <= 0:
        raise ValueError("price_per_unit must be > 0")
    if fees < 0:
        raise ValueError("fees cannot be negative")
    if base_asset_id == quote_asset_id:
        raise ValueError("base_asset_id and quote_asset_id must differ")

    # 1. Compute signed entry amounts. gross_quote is the unsigned notional.
    gross_quote_amount = quantity * price_per_unit
    if trade_side == TradeSide.BUY:
        base_amount = quantity
        quote_amount = -(gross_quote_amount + fees)
        transaction_type = TransactionType.BUY
    else:
        base_amount = -quantity
        quote_amount = gross_quote_amount - fees
        transaction_type = TransactionType.SELL

    # 2. Insert the trade row (quantity stays unsigned; side carries direction).
    trade = Trade(
        user_id=user_id,
        account_id=account_id,
        asset_id=base_asset_id,
        side=trade_side,
        quantity=quantity,
        price_per_unit=price_per_unit,
        fees=fees,
        executed_at=executed_at,
    )
    db.add(trade)
    await db.flush()

    # 3. Write the two balanced ledger entries via create_transaction.
    _ = await create_transaction(
        db,
        user_id=user_id,
        transaction_type=transaction_type,
        executed_at=executed_at,
        note=note,
        trade_id=trade.id,
        entry_inputs=[
            TransactionEntryInput(account_id=account_id, asset_id=base_asset_id, amount=base_amount),
            TransactionEntryInput(account_id=account_id, asset_id=quote_asset_id, amount=quote_amount),
        ],
    )

    return trade

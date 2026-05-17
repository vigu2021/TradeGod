from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.ledger.crud.trade import create_trade
from tradegod.ledger.models.account import Account
from tradegod.ledger.models.asset import Asset
from tradegod.ledger.models.trade import TradeSide
from tradegod.ledger.models.transaction import Transaction, TransactionType
from tradegod.ledger.models.transaction_entry import TransactionEntry
from tradegod.users.models import User

pytestmark = pytest.mark.asyncio


async def _entries_for_tx(db: AsyncSession, transaction_id: int) -> list[TransactionEntry]:
    result = await db.execute(select(TransactionEntry).where(TransactionEntry.transaction_id == transaction_id))
    return list(result.scalars().all())


async def _transaction_for_trade(db: AsyncSession, trade_id: int) -> Transaction:
    result = await db.execute(select(Transaction).where(Transaction.trade_id == trade_id))
    return result.scalar_one()


async def test_create_trade_buy_writes_balanced_rows(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset, aapl_asset: Asset
) -> None:
    executed_at = datetime.now(UTC)
    trade = await create_trade(
        db_session,
        user_id=user.id,
        account_id=account.id,
        base_asset_id=aapl_asset.id,
        quote_asset_id=usd_asset.id,
        trade_side=TradeSide.BUY,
        quantity=Decimal("10"),
        price_per_unit=Decimal("100"),
        executed_at=executed_at,
        fees=Decimal("5"),
        note="bought 10 AAPL",
    )

    assert trade.id is not None
    assert trade.side == TradeSide.BUY
    assert trade.quantity == Decimal("10")  # unsigned on trade row
    assert trade.price_per_unit == Decimal("100")
    assert trade.fees == Decimal("5")
    assert trade.executed_at == executed_at

    tx = await _transaction_for_trade(db_session, trade.id)
    assert tx.transaction_type == TransactionType.BUY
    assert tx.note == "bought 10 AAPL"
    assert tx.trade_id == trade.id

    entries = await _entries_for_tx(db_session, tx.id)
    by_asset = {e.asset_id: e.amount for e in entries}
    assert len(entries) == 2
    assert by_asset[aapl_asset.id] == Decimal("10")  # +qty
    assert by_asset[usd_asset.id] == Decimal("-1005")  # -(10*100 + 5)


async def test_create_trade_sell_inverts_signs(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset, aapl_asset: Asset
) -> None:
    trade = await create_trade(
        db_session,
        user_id=user.id,
        account_id=account.id,
        base_asset_id=aapl_asset.id,
        quote_asset_id=usd_asset.id,
        trade_side=TradeSide.SELL,
        quantity=Decimal("10"),
        price_per_unit=Decimal("100"),
        executed_at=datetime.now(UTC),
        fees=Decimal("5"),
    )

    assert trade.quantity == Decimal("10")  # still unsigned
    tx = await _transaction_for_trade(db_session, trade.id)
    assert tx.transaction_type == TransactionType.SELL

    entries = await _entries_for_tx(db_session, tx.id)
    by_asset = {e.asset_id: e.amount for e in entries}
    assert by_asset[aapl_asset.id] == Decimal("-10")  # -qty
    assert by_asset[usd_asset.id] == Decimal("995")  # +(10*100 - 5)


async def test_create_trade_no_fees_defaults_to_zero(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset, aapl_asset: Asset
) -> None:
    trade = await create_trade(
        db_session,
        user_id=user.id,
        account_id=account.id,
        base_asset_id=aapl_asset.id,
        quote_asset_id=usd_asset.id,
        trade_side=TradeSide.BUY,
        quantity=Decimal("2"),
        price_per_unit=Decimal("50"),
        executed_at=datetime.now(UTC),
    )

    assert trade.fees == Decimal("0")
    tx = await _transaction_for_trade(db_session, trade.id)
    entries = await _entries_for_tx(db_session, tx.id)
    by_asset = {e.asset_id: e.amount for e in entries}
    assert by_asset[usd_asset.id] == Decimal("-100")  # exact, no fee


async def test_create_trade_asset_for_asset_swap(
    db_session: AsyncSession, user: User, account: Account, aapl_asset: Asset
) -> None:
    # quote is a non-fiat asset (e.g. BTC/ETH crypto swap)
    btc = await _ensure_asset(db_session, "BTC", "Bitcoin")
    trade = await create_trade(
        db_session,
        user_id=user.id,
        account_id=account.id,
        base_asset_id=aapl_asset.id,
        quote_asset_id=btc.id,
        trade_side=TradeSide.BUY,
        quantity=Decimal("1"),
        price_per_unit=Decimal("0.5"),
        executed_at=datetime.now(UTC),
    )

    entries = await _entries_for_tx(db_session, (await _transaction_for_trade(db_session, trade.id)).id)
    by_asset = {e.asset_id: e.amount for e in entries}
    assert by_asset[aapl_asset.id] == Decimal("1")
    assert by_asset[btc.id] == Decimal("-0.5")


async def _ensure_asset(db: AsyncSession, symbol: str, name: str) -> Asset:
    from tradegod.ledger.models.asset import AssetType

    asset = Asset(asset_type=AssetType.CRYPTO, symbol=symbol, name=name)
    db.add(asset)
    await db.flush()
    return asset


# ---- validation -----------------------------------------------------------------

_BASE_KWARGS = dict(
    quantity=Decimal("1"),
    price_per_unit=Decimal("1"),
    fees=Decimal("0"),
    trade_side=TradeSide.BUY,
)


async def test_create_trade_quantity_zero_raises(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset, aapl_asset: Asset
) -> None:
    with pytest.raises(ValueError, match="quantity must be > 0"):
        await create_trade(
            db_session,
            user_id=user.id,
            account_id=account.id,
            base_asset_id=aapl_asset.id,
            quote_asset_id=usd_asset.id,
            trade_side=TradeSide.BUY,
            quantity=Decimal("0"),
            price_per_unit=Decimal("1"),
            executed_at=datetime.now(UTC),
        )


async def test_create_trade_negative_quantity_raises(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset, aapl_asset: Asset
) -> None:
    with pytest.raises(ValueError, match="quantity must be > 0"):
        await create_trade(
            db_session,
            user_id=user.id,
            account_id=account.id,
            base_asset_id=aapl_asset.id,
            quote_asset_id=usd_asset.id,
            trade_side=TradeSide.BUY,
            quantity=Decimal("-1"),
            price_per_unit=Decimal("1"),
            executed_at=datetime.now(UTC),
        )


async def test_create_trade_price_zero_raises(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset, aapl_asset: Asset
) -> None:
    with pytest.raises(ValueError, match="price_per_unit must be > 0"):
        await create_trade(
            db_session,
            user_id=user.id,
            account_id=account.id,
            base_asset_id=aapl_asset.id,
            quote_asset_id=usd_asset.id,
            trade_side=TradeSide.BUY,
            quantity=Decimal("1"),
            price_per_unit=Decimal("0"),
            executed_at=datetime.now(UTC),
        )


async def test_create_trade_negative_fees_raises(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset, aapl_asset: Asset
) -> None:
    with pytest.raises(ValueError, match="fees cannot be negative"):
        await create_trade(
            db_session,
            user_id=user.id,
            account_id=account.id,
            base_asset_id=aapl_asset.id,
            quote_asset_id=usd_asset.id,
            trade_side=TradeSide.BUY,
            quantity=Decimal("1"),
            price_per_unit=Decimal("1"),
            fees=Decimal("-0.01"),
            executed_at=datetime.now(UTC),
        )


async def test_create_trade_same_base_and_quote_raises(
    db_session: AsyncSession, user: User, account: Account, usd_asset: Asset
) -> None:
    with pytest.raises(ValueError, match="must differ"):
        await create_trade(
            db_session,
            user_id=user.id,
            account_id=account.id,
            base_asset_id=usd_asset.id,
            quote_asset_id=usd_asset.id,
            trade_side=TradeSide.BUY,
            quantity=Decimal("1"),
            price_per_unit=Decimal("1"),
            executed_at=datetime.now(UTC),
        )

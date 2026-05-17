from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tradegod.core.database import Base, sql_enum
from tradegod.ledger.models.account import Account
from tradegod.ledger.models.asset import Asset
from tradegod.users.models import User


class TradeSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False)
    side: Mapped[TradeSide] = mapped_column(sql_enum(TradeSide, name="trade_side_enum"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(28, 18), nullable=False)
    price_per_unit: Mapped[Decimal] = mapped_column(Numeric(28, 18), nullable=False)
    fees: Mapped[Decimal] = mapped_column(Numeric(28, 18), nullable=False, default=Decimal("0"), server_default="0")
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(lazy="raise")
    account: Mapped[Account] = relationship(lazy="raise")
    asset: Mapped[Asset] = relationship(lazy="raise")

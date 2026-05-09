from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tradegod.core.database import Base
from tradegod.ledger.models.account import Account
from tradegod.ledger.models.asset import Asset


class AccountHolding(Base):
    __tablename__ = "account_holdings"
    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "asset_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(28, 18), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    account: Mapped[Account] = relationship(lazy="raise")
    asset: Mapped[Asset] = relationship(lazy="raise")

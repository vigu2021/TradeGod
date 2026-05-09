from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tradegod.core.database import Base
from tradegod.ledger.models.account import Account
from tradegod.ledger.models.asset import Asset
from tradegod.ledger.models.transaction import Transaction


class TransactionEntry(Base):
    __tablename__ = "transaction_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(28, 18), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    transaction: Mapped[Transaction] = relationship(lazy="raise")
    account: Mapped[Account] = relationship(lazy="raise")
    asset: Mapped[Asset] = relationship(lazy="raise")

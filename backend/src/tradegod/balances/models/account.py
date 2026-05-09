from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, String, func, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tradegod.core.database import Base, sql_enum
from tradegod.users.models import User


class AccountType(StrEnum):
    CASH = "cash"
    BANK = "bank"
    BROKERAGE = "brokerage"
    CRYPTO_EXCHANGE = "crypto_exchange"
    WALLET = "wallet"


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("user_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    account_type: Mapped[AccountType] = mapped_column(sql_enum(AccountType, name="account_type_enum"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(lazy = "raise")

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from tradegod.core.database import Base, sql_enum


class AssetType(StrEnum):
    FIAT = "fiat"
    STOCK = "stock"
    CRYPTO = "crypto"
    FUTURE = "future"


class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_type: Mapped[AssetType] = mapped_column(sql_enum(AssetType, name="asset_type_enum"), nullable=False)
    asset_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

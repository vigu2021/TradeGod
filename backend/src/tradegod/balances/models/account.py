from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tradegod.core.database import Base


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

"""API Key model for authentication."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.common import IntPK, TimestampWithDeleteMixin

if TYPE_CHECKING:
    from src.models.prediction_log import PredictionLog


class APIKey(Base, TimestampWithDeleteMixin):
    """Stores API keys for authentication. Keys are hashed, never stored in plain text."""

    __tablename__ = "api_keys"

    id: Mapped[IntPK]
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    key_prefix: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    prediction_logs: Mapped[list["PredictionLog"]] = relationship(
        "PredictionLog", back_populates="api_key", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name='{self.name}', active={self.is_active})>"

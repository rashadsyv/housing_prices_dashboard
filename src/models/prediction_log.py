"""Prediction Log model for audit trail."""

from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.common import IntPK, TimestampMixin

if TYPE_CHECKING:
    from src.models.api_key import APIKey


class PredictionLog(Base, TimestampMixin):
    """Stores prediction requests and results for audit trail and analytics."""

    __tablename__ = "prediction_logs"

    id: Mapped[IntPK]
    api_key_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("api_keys.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    input_features: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    predicted_price: Mapped[float] = mapped_column(Float, nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    request_type: Mapped[str] = mapped_column(
        String(10), default="single", nullable=False
    )
    batch_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    api_key: Mapped["APIKey"] = relationship("APIKey", back_populates="prediction_logs")

    def __repr__(self) -> str:
        return f"<PredictionLog(id={self.id}, price=${self.predicted_price:,.2f})>"

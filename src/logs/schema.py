"""Pydantic schemas for prediction logs."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class PredictionLogResponse(BaseModel):
    id: int
    api_key_id: int | None = None
    input_features: dict[str, Any]
    predicted_price: float
    response_time_ms: int | None = None
    request_type: str
    batch_id: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PredictionLogListResponse(BaseModel):
    logs: list[PredictionLogResponse]
    total: int
    skip: int
    limit: int


class PredictionStatsResponse(BaseModel):
    total_predictions: int
    predictions_by_user: int

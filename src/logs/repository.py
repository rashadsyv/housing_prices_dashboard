"""Repository for prediction log operations."""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models import PredictionLog


class PredictionLogRepository:
    """Repository for prediction log CRUD operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        api_key_id: int,
        input_features: dict[str, Any],
        predicted_price: float,
        response_time_ms: int | None = None,
        request_type: str = "single",
        batch_id: str | None = None,
    ) -> PredictionLog:
        log = PredictionLog(
            api_key_id=api_key_id,
            input_features=input_features,
            predicted_price=predicted_price,
            response_time_ms=response_time_ms,
            request_type=request_type,
            batch_id=batch_id,
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def create_batch(
        self,
        api_key_id: int,
        predictions: list[tuple[dict[str, Any], float]],
        response_time_ms: int | None = None,
    ) -> list[PredictionLog]:
        batch_id = str(uuid.uuid4())
        logs = []

        for input_features, predicted_price in predictions:
            log = PredictionLog(
                api_key_id=api_key_id,
                input_features=input_features,
                predicted_price=predicted_price,
                response_time_ms=response_time_ms,
                request_type="batch",
                batch_id=batch_id,
            )
            self.session.add(log)
            logs.append(log)

        self.session.commit()
        for log in logs:
            self.session.refresh(log)

        return logs

    def get_by_id(self, log_id: int) -> PredictionLog | None:
        stmt = select(PredictionLog).where(PredictionLog.id == log_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_api_key(
        self, api_key_id: int, skip: int = 0, limit: int = 100
    ) -> list[PredictionLog]:
        stmt = (
            select(PredictionLog)
            .where(PredictionLog.api_key_id == api_key_id)
            .order_by(PredictionLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_batch_id(self, batch_id: str) -> list[PredictionLog]:
        stmt = (
            select(PredictionLog)
            .where(PredictionLog.batch_id == batch_id)
            .order_by(PredictionLog.created_at)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_recent(self, limit: int = 100) -> list[PredictionLog]:
        stmt = (
            select(PredictionLog).order_by(PredictionLog.created_at.desc()).limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def count_by_api_key(self, api_key_id: int) -> int:
        stmt = select(func.count(PredictionLog.id)).where(
            PredictionLog.api_key_id == api_key_id
        )
        return self.session.execute(stmt).scalar() or 0

    def count_all(self) -> int:
        stmt = select(func.count(PredictionLog.id))
        return self.session.execute(stmt).scalar() or 0

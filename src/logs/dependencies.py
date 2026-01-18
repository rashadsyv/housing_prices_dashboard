"""Prediction log dependencies for FastAPI."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.logs.repository import PredictionLogRepository

DbSessionDep = Annotated[Session, Depends(get_db)]


def get_prediction_log_repo(session: DbSessionDep) -> PredictionLogRepository:
    return PredictionLogRepository(session)


PredictionLogRepoDep = Annotated[
    PredictionLogRepository, Depends(get_prediction_log_repo)
]

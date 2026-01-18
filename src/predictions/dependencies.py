"""Prediction dependencies for FastAPI."""

from typing import Annotated

from fastapi import Depends

from src.logs.dependencies import PredictionLogRepoDep
from src.predictions.service import PredictionService


def get_prediction_service(log_repo: PredictionLogRepoDep) -> PredictionService:
    return PredictionService(log_repo)


PredictionServiceDep = Annotated[PredictionService, Depends(get_prediction_service)]

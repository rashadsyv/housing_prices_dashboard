"""Prediction logs API routes."""

import logging

from fastapi import APIRouter, HTTPException, status

from src.auth.dependencies import CurrentUserDep
from src.logs.dependencies import PredictionLogRepoDep
from src.logs.schema import (
    PredictionLogListResponse,
    PredictionLogResponse,
    PredictionStatsResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "", response_model=PredictionLogListResponse, summary="Get My Prediction Logs"
)
async def get_my_logs(
    current_user: CurrentUserDep,
    repo: PredictionLogRepoDep,
    skip: int = 0,
    limit: int = 100,
) -> PredictionLogListResponse:
    logs = repo.get_by_api_key(current_user["id"], skip=skip, limit=limit)
    total = repo.count_by_api_key(current_user["id"])
    return PredictionLogListResponse(
        logs=[PredictionLogResponse.model_validate(log) for log in logs],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/stats",
    response_model=PredictionStatsResponse,
    summary="Get Prediction Statistics",
)
async def get_stats(
    current_user: CurrentUserDep, repo: PredictionLogRepoDep
) -> PredictionStatsResponse:
    return PredictionStatsResponse(
        total_predictions=repo.count_all(),
        predictions_by_user=repo.count_by_api_key(current_user["id"]),
    )


@router.get(
    "/{log_id}",
    response_model=PredictionLogResponse,
    summary="Get Prediction Log by ID",
)
async def get_log_by_id(
    log_id: int,
    current_user: CurrentUserDep,
    repo: PredictionLogRepoDep,
) -> PredictionLogResponse:
    log = repo.get_by_id(log_id)

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prediction log not found"
        )

    if log.api_key_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this log",
        )

    return PredictionLogResponse.model_validate(log)

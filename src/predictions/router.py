"""Prediction API routes."""

import logging

from fastapi import APIRouter, HTTPException, Request, status

from src.auth.dependencies import CurrentUserDep
from src.core.exceptions import PredictionError
from src.core.rate_limiter import get_rate_limit_string, limiter
from src.predictions.dependencies import PredictionServiceDep
from src.predictions.schema import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    HouseFeatures,
    PredictionResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=PredictionResponse,
    summary="Predict House Price",
    description="Predict the median house value based on property features.",
)
@limiter.limit(get_rate_limit_string())
async def predict_price(
    request: Request,
    features: HouseFeatures,
    current_user: CurrentUserDep,
    service: PredictionServiceDep,
) -> PredictionResponse:
    logger.info(f"Prediction request from user: {current_user['name']}")
    try:
        result = service.predict(features, api_key_id=current_user["id"])
        logger.info(f"Prediction: ${result.predicted_price:,.2f}")
        return result
    except PredictionError as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.post(
    "/batch",
    response_model=BatchPredictionResponse,
    summary="Batch Predict House Prices",
    description="Predict median house values for multiple properties (max 100).",
)
@limiter.limit(get_rate_limit_string())
async def predict_batch(
    request: Request,
    batch_request: BatchPredictionRequest,
    current_user: CurrentUserDep,
    service: PredictionServiceDep,
) -> BatchPredictionResponse:
    logger.info(
        f"Batch prediction: {len(batch_request.houses)} houses from {current_user['name']}"
    )
    try:
        result = service.predict_batch(
            batch_request.houses, api_key_id=current_user["id"]
        )
        logger.info(f"Batch complete: {result.count} predictions")
        return result
    except PredictionError as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e

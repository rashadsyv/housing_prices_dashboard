"""Service for housing price predictions using the ML model."""

import logging
import time
from typing import TYPE_CHECKING

from src.core.exceptions import PredictionError
from src.ml.model import load_model
from src.ml.preprocessing import prepare_batch_features, prepare_features
from src.predictions.schema import (
    BatchPredictionResponse,
    HouseFeatures,
    PredictionResponse,
)

if TYPE_CHECKING:
    from src.logs.repository import PredictionLogRepository

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for making housing price predictions."""

    def __init__(self, log_repo: "PredictionLogRepository | None" = None) -> None:
        self.model = load_model()
        self.log_repo = log_repo

    def predict(
        self, features: HouseFeatures, api_key_id: int | None = None
    ) -> PredictionResponse:
        """Predict the price for a single house."""
        start_time = time.time()

        try:
            X = prepare_features(features)
            prediction = self.model.predict(X)
            predicted_price = round(float(prediction[0]), 8)
            response_time_ms = int((time.time() - start_time) * 1000)

            if self.log_repo and api_key_id:
                self.log_repo.create(
                    api_key_id=api_key_id,
                    input_features=features.model_dump(),
                    predicted_price=predicted_price,
                    response_time_ms=response_time_ms,
                    request_type="single",
                )

            return PredictionResponse(predicted_price=predicted_price)

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise PredictionError(f"Prediction failed: {e}") from e

    def predict_batch(
        self, features_list: list[HouseFeatures], api_key_id: int | None = None
    ) -> BatchPredictionResponse:
        """Predict prices for multiple houses."""
        start_time = time.time()

        try:
            X = prepare_batch_features(features_list)
            predictions = self.model.predict(X)
            response_time_ms = int((time.time() - start_time) * 1000)

            results = [
                PredictionResponse(predicted_price=round(float(p), 8))
                for p in predictions
            ]

            if self.log_repo and api_key_id:
                prediction_data = [
                    (features.model_dump(), float(price))
                    for features, price in zip(features_list, predictions, strict=False)
                ]
                self.log_repo.create_batch(
                    api_key_id=api_key_id,
                    predictions=prediction_data,
                    response_time_ms=response_time_ms,
                )

            return BatchPredictionResponse(predictions=results, count=len(results))

        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            raise PredictionError(f"Batch prediction failed: {e}") from e

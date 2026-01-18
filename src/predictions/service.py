"""Service for housing price predictions using the ML model."""

import logging
import time
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

import joblib
import pandas as pd

from src.config import settings
from src.constants import ALL_FEATURE_COLUMNS, OCEAN_PROXIMITY_COLUMNS
from src.predictions.schema import (
    BatchPredictionResponse,
    HouseFeatures,
    PredictionResponse,
)

if TYPE_CHECKING:
    from src.logs.repository import PredictionLogRepository

logger = logging.getLogger(__name__)


class ModelLoadError(Exception):
    """Raised when the ML model cannot be loaded."""

    pass


class PredictionError(Exception):
    """Raised when prediction fails."""

    pass


@lru_cache(maxsize=1)
def load_model():
    """Load the ML model from disk. Cached to load only once."""
    model_path = Path(settings.MODEL_PATH)

    if not model_path.exists():
        raise ModelLoadError(f"Model file not found: {model_path}")

    try:
        logger.info(f"Loading model from: {model_path}")
        model = joblib.load(model_path)
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise ModelLoadError(f"Failed to load model: {e}") from e


def _prepare_features(features: HouseFeatures) -> pd.DataFrame:
    """Convert HouseFeatures to DataFrame for model input."""
    data = {
        "longitude": features.longitude,
        "latitude": features.latitude,
        "housing_median_age": features.housing_median_age,
        "total_rooms": features.total_rooms,
        "total_bedrooms": features.total_bedrooms,
        "population": features.population,
        "households": features.households,
        "median_income": features.median_income,
    }

    # One-hot encode ocean_proximity
    for col in OCEAN_PROXIMITY_COLUMNS:
        category = col.replace("ocean_proximity_", "")
        data[col] = 1.0 if features.ocean_proximity.value == category else 0.0

    return pd.DataFrame([data], columns=ALL_FEATURE_COLUMNS)


def _prepare_batch_features(features_list: list[HouseFeatures]) -> pd.DataFrame:
    """Convert list of HouseFeatures to DataFrame for batch prediction."""
    rows = []
    for features in features_list:
        data = {
            "longitude": features.longitude,
            "latitude": features.latitude,
            "housing_median_age": features.housing_median_age,
            "total_rooms": features.total_rooms,
            "total_bedrooms": features.total_bedrooms,
            "population": features.population,
            "households": features.households,
            "median_income": features.median_income,
        }
        for col in OCEAN_PROXIMITY_COLUMNS:
            category = col.replace("ocean_proximity_", "")
            data[col] = 1.0 if features.ocean_proximity.value == category else 0.0
        rows.append(data)

    return pd.DataFrame(rows, columns=ALL_FEATURE_COLUMNS)


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
            X = _prepare_features(features)
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
            X = _prepare_batch_features(features_list)
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

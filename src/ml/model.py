"""ML model loading and caching."""

import logging
from functools import lru_cache
from pathlib import Path

import joblib

from src.config import settings
from src.core.exceptions import ModelLoadError

logger = logging.getLogger(__name__)


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

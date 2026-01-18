"""Application constants for ML features and API configuration."""

# Feature columns expected by the model (must match training order)
NUMERIC_FEATURES: list[str] = [
    "longitude",
    "latitude",
    "housing_median_age",
    "total_rooms",
    "total_bedrooms",
    "population",
    "households",
    "median_income",
]

OCEAN_PROXIMITY_COLUMNS: list[str] = [
    "ocean_proximity_<1H OCEAN",
    "ocean_proximity_INLAND",
    "ocean_proximity_ISLAND",
    "ocean_proximity_NEAR BAY",
    "ocean_proximity_NEAR OCEAN",
]

ALL_FEATURE_COLUMNS: list[str] = NUMERIC_FEATURES + OCEAN_PROXIMITY_COLUMNS

# Valid ocean proximity values for input validation
OCEAN_PROXIMITY_VALUES: list[str] = [
    "<1H OCEAN",
    "INLAND",
    "ISLAND",
    "NEAR BAY",
    "NEAR OCEAN",
]

# Model configuration
DEFAULT_MODEL_PATH: str = "model.joblib"

# API limits
MAX_BATCH_SIZE: int = 100
DEFAULT_RATE_LIMIT_PER_MINUTE: int = 100
API_KEY_CREATE_LIMIT: str = "10/hour"
TOKEN_REQUEST_LIMIT: str = "30/minute"

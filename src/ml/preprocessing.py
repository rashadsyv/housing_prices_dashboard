"""Feature engineering and preprocessing for ML model input."""

import pandas as pd

from src.constants import ALL_FEATURE_COLUMNS, OCEAN_PROXIMITY_COLUMNS
from src.predictions.schema import HouseFeatures


def prepare_features(features: HouseFeatures) -> pd.DataFrame:
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

    for col in OCEAN_PROXIMITY_COLUMNS:
        category = col.replace("ocean_proximity_", "")
        data[col] = 1.0 if features.ocean_proximity.value == category else 0.0

    return pd.DataFrame([data], columns=ALL_FEATURE_COLUMNS)


def prepare_batch_features(features_list: list[HouseFeatures]) -> pd.DataFrame:
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

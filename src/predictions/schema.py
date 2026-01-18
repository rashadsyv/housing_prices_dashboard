"""Pydantic schemas for housing price predictions."""

from enum import Enum

from pydantic import BaseModel, Field


class OceanProximity(str, Enum):
    NEAR_BAY = "NEAR BAY"
    NEAR_OCEAN = "NEAR OCEAN"
    INLAND = "INLAND"
    LESS_THAN_1H_OCEAN = "<1H OCEAN"
    ISLAND = "ISLAND"


class HouseFeatures(BaseModel):
    """Input features for house price prediction."""

    longitude: float = Field(..., ge=-180, le=180, examples=[-122.64])
    latitude: float = Field(..., ge=-90, le=90, examples=[38.01])
    housing_median_age: float = Field(..., ge=0, le=100, examples=[36.0])
    total_rooms: float = Field(..., ge=0, examples=[1336.0])
    total_bedrooms: float = Field(..., ge=0, examples=[258.0])
    population: float = Field(..., ge=0, examples=[678.0])
    households: float = Field(..., ge=0, examples=[249.0])
    median_income: float = Field(..., ge=0, examples=[5.5789])
    ocean_proximity: OceanProximity = Field(..., examples=["NEAR OCEAN"])


class PredictionResponse(BaseModel):
    predicted_price: float = Field(..., examples=[320201.59])
    currency: str = Field(default="USD")


class BatchPredictionRequest(BaseModel):
    houses: list[HouseFeatures] = Field(..., min_length=1, max_length=100)


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]
    count: int

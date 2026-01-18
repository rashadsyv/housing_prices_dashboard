"""Unit tests for Pydantic schemas - validation without database."""

import pytest
from pydantic import ValidationError

from src.auth.schema import APIKeyCreate, TokenRequest
from src.predictions.schema import BatchPredictionRequest, HouseFeatures


class TestAPIKeySchemas:
    """Test API key schemas validation."""

    def test_api_key_create_valid(self):
        """Test valid API key creation schema."""
        data = APIKeyCreate(name="Test Key", description="A test key")
        assert data.name == "Test Key"
        assert data.description == "A test key"

    def test_api_key_create_without_description(self):
        """Test API key creation without description."""
        data = APIKeyCreate(name="Test Key")
        assert data.name == "Test Key"
        assert data.description is None

    def test_api_key_create_empty_name_fails(self):
        """Test API key creation with empty name fails."""
        with pytest.raises(ValidationError) as exc_info:
            APIKeyCreate(name="")
        assert "at least 1 character" in str(exc_info.value).lower()

    def test_api_key_create_whitespace_name_allowed(self):
        """Test API key creation with whitespace-only name is allowed (no strip)."""
        # Note: min_length=1 doesn't strip whitespace, so "   " passes
        # This is acceptable as the API can handle it
        data = APIKeyCreate(name="   ")
        assert data.name == "   "

    def test_api_key_create_long_name_fails(self):
        """Test API key creation with too long name fails."""
        with pytest.raises(ValidationError):
            APIKeyCreate(name="x" * 101)  # Max 100 chars


class TestTokenSchemas:
    """Test token request schemas."""

    def test_token_request_valid(self):
        """Test valid token request."""
        data = TokenRequest(api_key="valid-api-key-123")
        assert data.api_key == "valid-api-key-123"

    def test_token_request_empty_key_fails(self):
        """Test token request with empty key fails."""
        with pytest.raises(ValidationError):
            TokenRequest(api_key="")


class TestHouseFeaturesSchema:
    """Test house features schema validation."""

    @pytest.fixture
    def valid_features(self) -> dict:
        """Valid house features."""
        return {
            "longitude": -122.64,
            "latitude": 38.01,
            "housing_median_age": 36.0,
            "total_rooms": 1336.0,
            "total_bedrooms": 258.0,
            "population": 678.0,
            "households": 249.0,
            "median_income": 5.5789,
            "ocean_proximity": "NEAR OCEAN",
        }

    def test_valid_features(self, valid_features):
        """Test valid house features pass validation."""
        data = HouseFeatures(**valid_features)
        assert data.longitude == -122.64
        assert data.ocean_proximity == "NEAR OCEAN"

    def test_invalid_longitude_too_low(self, valid_features):
        """Test longitude below -180 fails."""
        valid_features["longitude"] = -200
        with pytest.raises(ValidationError) as exc_info:
            HouseFeatures(**valid_features)
        assert "longitude" in str(exc_info.value).lower()

    def test_invalid_longitude_too_high(self, valid_features):
        """Test longitude above 180 fails."""
        valid_features["longitude"] = 200
        with pytest.raises(ValidationError) as exc_info:
            HouseFeatures(**valid_features)
        assert "longitude" in str(exc_info.value).lower()

    def test_invalid_latitude_too_low(self, valid_features):
        """Test latitude below -90 fails."""
        valid_features["latitude"] = -100
        with pytest.raises(ValidationError) as exc_info:
            HouseFeatures(**valid_features)
        assert "latitude" in str(exc_info.value).lower()

    def test_invalid_latitude_too_high(self, valid_features):
        """Test latitude above 90 fails."""
        valid_features["latitude"] = 100
        with pytest.raises(ValidationError) as exc_info:
            HouseFeatures(**valid_features)
        assert "latitude" in str(exc_info.value).lower()

    def test_negative_rooms_fails(self, valid_features):
        """Test negative total rooms fails."""
        valid_features["total_rooms"] = -100
        with pytest.raises(ValidationError):
            HouseFeatures(**valid_features)

    def test_negative_bedrooms_fails(self, valid_features):
        """Test negative bedrooms fails."""
        valid_features["total_bedrooms"] = -1
        with pytest.raises(ValidationError):
            HouseFeatures(**valid_features)

    def test_negative_population_fails(self, valid_features):
        """Test negative population fails."""
        valid_features["population"] = -1
        with pytest.raises(ValidationError):
            HouseFeatures(**valid_features)

    def test_negative_households_fails(self, valid_features):
        """Test negative households fails."""
        valid_features["households"] = -1
        with pytest.raises(ValidationError):
            HouseFeatures(**valid_features)

    def test_negative_income_fails(self, valid_features):
        """Test negative income fails."""
        valid_features["median_income"] = -1
        with pytest.raises(ValidationError):
            HouseFeatures(**valid_features)

    def test_invalid_ocean_proximity(self, valid_features):
        """Test invalid ocean proximity value fails."""
        valid_features["ocean_proximity"] = "INVALID"
        with pytest.raises(ValidationError) as exc_info:
            HouseFeatures(**valid_features)
        assert "ocean_proximity" in str(exc_info.value).lower()

    @pytest.mark.parametrize(
        "ocean_proximity",
        ["NEAR BAY", "NEAR OCEAN", "INLAND", "<1H OCEAN", "ISLAND"],
    )
    def test_all_valid_ocean_proximity_values(self, valid_features, ocean_proximity):
        """Test all valid ocean proximity values are accepted."""
        valid_features["ocean_proximity"] = ocean_proximity
        data = HouseFeatures(**valid_features)
        assert data.ocean_proximity == ocean_proximity

    def test_missing_required_field(self):
        """Test missing required field fails."""
        with pytest.raises(ValidationError):
            HouseFeatures(longitude=-122.64, latitude=38.01)


class TestBatchPredictionSchema:
    """Test batch prediction request schema."""

    @pytest.fixture
    def valid_house(self) -> dict:
        """Valid house features."""
        return {
            "longitude": -122.64,
            "latitude": 38.01,
            "housing_median_age": 36.0,
            "total_rooms": 1336.0,
            "total_bedrooms": 258.0,
            "population": 678.0,
            "households": 249.0,
            "median_income": 5.5789,
            "ocean_proximity": "NEAR OCEAN",
        }

    def test_valid_batch_request(self, valid_house):
        """Test valid batch request."""
        data = BatchPredictionRequest(houses=[valid_house, valid_house])
        assert len(data.houses) == 2

    def test_empty_batch_fails(self):
        """Test empty batch request fails."""
        with pytest.raises(ValidationError):
            BatchPredictionRequest(houses=[])

    def test_batch_exceeds_max_size(self, valid_house):
        """Test batch exceeding max size fails."""
        with pytest.raises(ValidationError):
            BatchPredictionRequest(houses=[valid_house] * 101)  # Max 100

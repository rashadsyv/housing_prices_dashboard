"""Unit tests for configuration - no external dependencies."""


from src.config import settings
from src.constants import (
    ALL_FEATURE_COLUMNS,
    DEFAULT_MODEL_PATH,
    MAX_BATCH_SIZE,
    NUMERIC_FEATURES,
    OCEAN_PROXIMITY_COLUMNS,
    OCEAN_PROXIMITY_VALUES,
)


class TestSettings:
    """Test application settings."""

    def test_settings_instance_exists(self):
        """Test settings singleton exists."""
        assert settings is not None

    def test_settings_has_required_fields(self):
        """Test settings has all required fields."""
        assert hasattr(settings, "PROJECT_NAME")
        assert hasattr(settings, "VERSION")
        assert hasattr(settings, "SECRET_KEY")
        assert hasattr(settings, "ALGORITHM")
        assert hasattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES")
        assert hasattr(settings, "RATE_LIMIT_PER_MINUTE")
        assert hasattr(settings, "DATABASE_URL")
        assert hasattr(settings, "LOG_LEVEL")
        assert hasattr(settings, "ENVIRONMENT")

    def test_settings_default_values(self):
        """Test settings have sensible defaults."""
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.RATE_LIMIT_PER_MINUTE > 0

    def test_is_production_property(self):
        """Test is_production property works."""
        assert isinstance(settings.is_production, bool)

    def test_project_name(self):
        """Test project name is set."""
        assert "Housing" in settings.PROJECT_NAME


class TestConstants:
    """Test application constants."""

    def test_numeric_features_count(self):
        """Test correct number of numeric features."""
        assert len(NUMERIC_FEATURES) == 8

    def test_numeric_features_content(self):
        """Test numeric features contain expected values."""
        expected = [
            "longitude",
            "latitude",
            "housing_median_age",
            "total_rooms",
            "total_bedrooms",
            "population",
            "households",
            "median_income",
        ]
        assert NUMERIC_FEATURES == expected

    def test_ocean_proximity_values(self):
        """Test ocean proximity values are correct."""
        expected = ["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]
        assert sorted(OCEAN_PROXIMITY_VALUES) == sorted(expected)

    def test_ocean_proximity_columns_count(self):
        """Test correct number of ocean proximity columns."""
        assert len(OCEAN_PROXIMITY_COLUMNS) == 5

    def test_ocean_proximity_columns_format(self):
        """Test ocean proximity columns have correct prefix."""
        for col in OCEAN_PROXIMITY_COLUMNS:
            assert col.startswith("ocean_proximity_")

    def test_all_feature_columns_total(self):
        """Test total feature columns count."""
        expected_count = len(NUMERIC_FEATURES) + len(OCEAN_PROXIMITY_COLUMNS)
        assert len(ALL_FEATURE_COLUMNS) == expected_count

    def test_max_batch_size(self):
        """Test max batch size is reasonable."""
        assert MAX_BATCH_SIZE == 100
        assert MAX_BATCH_SIZE > 0

    def test_default_model_path(self):
        """Test default model path."""
        assert DEFAULT_MODEL_PATH == "model.joblib"
        assert DEFAULT_MODEL_PATH.endswith(".joblib")

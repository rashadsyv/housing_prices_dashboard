"""Integration tests for prediction API endpoints.

These tests require the full application stack including:
- Database connection
- ML model loaded
- FastAPI application
- All middleware
"""

import pytest
from fastapi.testclient import TestClient


class TestSinglePredictionAPI:
    """Integration tests for single prediction endpoint."""

    def test_predict_success(
        self, client: TestClient, auth_headers: dict, sample_house_features: dict
    ):
        """Test successful prediction via API."""
        response = client.post(
            "/predict", json=sample_house_features, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "predicted_price" in data
        assert data["currency"] == "USD"
        assert data["predicted_price"] > 0

    def test_predict_sample_1_accuracy(
        self, client: TestClient, auth_headers: dict, sample_house_features: dict
    ):
        """
        Test prediction accuracy for sample input 1.

        Expected output: 320201.58554044
        """
        response = client.post(
            "/predict", json=sample_house_features, headers=auth_headers
        )

        assert response.status_code == 200
        predicted = response.json()["predicted_price"]
        expected = 320201.58554044

        assert predicted == expected, f"Expected {expected}, got {predicted}"

    def test_predict_sample_2_accuracy(
        self, client: TestClient, auth_headers: dict, sample_house_features_2: dict
    ):
        """
        Test prediction accuracy for sample input 2.

        Expected output: 58815.45033765
        """
        response = client.post(
            "/predict", json=sample_house_features_2, headers=auth_headers
        )

        assert response.status_code == 200
        predicted = response.json()["predicted_price"]
        expected = 58815.45033765

        assert predicted == expected, f"Expected {expected}, got {predicted}"

    def test_predict_sample_3_accuracy(
        self, client: TestClient, auth_headers: dict, sample_house_features_3: dict
    ):
        """
        Test prediction accuracy for sample input 3.

        Expected output: 192575.77355635
        """
        response = client.post(
            "/predict", json=sample_house_features_3, headers=auth_headers
        )

        assert response.status_code == 200
        predicted = response.json()["predicted_price"]
        expected = 192575.77355635

        assert predicted == expected, f"Expected {expected}, got {predicted}"

    def test_predict_unauthorized(
        self, client: TestClient, sample_house_features: dict
    ):
        """Test prediction without authentication fails via API."""
        response = client.post("/predict", json=sample_house_features)
        assert response.status_code == 403

    def test_predict_invalid_ocean_proximity(
        self, client: TestClient, auth_headers: dict, sample_house_features: dict
    ):
        """Test prediction with invalid ocean_proximity fails via API."""
        sample_house_features["ocean_proximity"] = "INVALID"
        response = client.post(
            "/predict", json=sample_house_features, headers=auth_headers
        )
        assert response.status_code == 422

    def test_predict_missing_field(self, client: TestClient, auth_headers: dict):
        """Test prediction with missing field fails via API."""
        incomplete_features = {
            "longitude": -122.64,
            "latitude": 38.01,
            # Missing other required fields
        }
        response = client.post(
            "/predict", json=incomplete_features, headers=auth_headers
        )
        assert response.status_code == 422

    def test_predict_invalid_longitude(
        self, client: TestClient, auth_headers: dict, sample_house_features: dict
    ):
        """Test prediction with invalid longitude fails via API."""
        sample_house_features["longitude"] = 200  # Invalid: must be -180 to 180
        response = client.post(
            "/predict", json=sample_house_features, headers=auth_headers
        )
        assert response.status_code == 422

    def test_predict_negative_rooms(
        self, client: TestClient, auth_headers: dict, sample_house_features: dict
    ):
        """Test prediction with negative rooms fails via API."""
        sample_house_features["total_rooms"] = -100
        response = client.post(
            "/predict", json=sample_house_features, headers=auth_headers
        )
        assert response.status_code == 422


class TestBatchPredictionAPI:
    """Integration tests for batch prediction endpoint."""

    def test_batch_predict_success(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_house_features: dict,
        sample_house_features_2: dict,
    ):
        """Test successful batch prediction via API."""
        response = client.post(
            "/predict/batch",
            json={"houses": [sample_house_features, sample_house_features_2]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert data["count"] == 2
        assert len(data["predictions"]) == 2

    def test_batch_predict_all_samples_accuracy(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_house_features: dict,
        sample_house_features_2: dict,
        sample_house_features_3: dict,
    ):
        """Test batch prediction accuracy with all sample inputs."""
        response = client.post(
            "/predict/batch",
            json={
                "houses": [
                    sample_house_features,
                    sample_house_features_2,
                    sample_house_features_3,
                ]
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3

        expected = [320201.58554044, 58815.45033765, 192575.77355635]
        for i, prediction in enumerate(data["predictions"]):
            predicted = prediction["predicted_price"]
            assert predicted == expected[i], (
                f"Sample {i + 1}: Expected {expected[i]}, got {predicted}"
            )

    def test_batch_predict_empty_list(self, client: TestClient, auth_headers: dict):
        """Test batch prediction with empty list fails via API."""
        response = client.post(
            "/predict/batch", json={"houses": []}, headers=auth_headers
        )
        assert response.status_code == 422

    def test_batch_predict_unauthorized(
        self, client: TestClient, sample_house_features: dict
    ):
        """Test batch prediction without authentication fails via API."""
        response = client.post(
            "/predict/batch", json={"houses": [sample_house_features]}
        )
        assert response.status_code == 403


class TestOceanProximityValuesAPI:
    """Integration tests for all valid ocean proximity values via API."""

    @pytest.mark.parametrize(
        "ocean_proximity",
        ["NEAR BAY", "NEAR OCEAN", "INLAND", "<1H OCEAN", "ISLAND"],
    )
    def test_all_ocean_proximity_values(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_house_features: dict,
        ocean_proximity: str,
    ):
        """Test prediction works with all valid ocean proximity values via API."""
        sample_house_features["ocean_proximity"] = ocean_proximity
        response = client.post(
            "/predict", json=sample_house_features, headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["predicted_price"] > 0

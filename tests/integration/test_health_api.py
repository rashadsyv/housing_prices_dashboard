"""Integration tests for health check API endpoints.

These tests require the full application stack including:
- Database connection
- ML model loaded
- FastAPI application
- All middleware
"""

from fastapi.testclient import TestClient


class TestHealthEndpointsAPI:
    """Integration tests for health check endpoints."""

    def test_health_check_returns_200(self, client: TestClient):
        """Test basic health check returns 200 via API."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data

    def test_health_check_includes_version(self, client: TestClient):
        """Test health check includes version information via API."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"

    def test_detailed_health_check(self, client: TestClient):
        """Test detailed health check returns component status via API."""
        response = client.get("/health/detailed")

        assert response.status_code == 200
        data = response.json()
        assert "components" in data
        assert "database" in data["components"]
        assert "model" in data["components"]

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns welcome message via API."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert data["docs"] == "/docs"


class TestMiddlewareAPI:
    """Integration tests for middleware functionality."""

    def test_correlation_id_present(self, client: TestClient):
        """Test correlation ID is present in response headers."""
        response = client.get("/health")
        assert "x-correlation-id" in response.headers

    def test_response_time_present(self, client: TestClient):
        """Test response time is present in response headers."""
        response = client.get("/health")
        assert "x-response-time" in response.headers

    def test_correlation_id_format(self, client: TestClient):
        """Test correlation ID has correct format (8 chars)."""
        response = client.get("/health")
        correlation_id = response.headers["x-correlation-id"]
        assert len(correlation_id) == 8  # UUID first 8 chars

    def test_response_time_format(self, client: TestClient):
        """Test response time has correct format (ends with ms)."""
        response = client.get("/health")
        response_time = response.headers["x-response-time"]
        assert response_time.endswith("ms")


class TestCORSAPI:
    """Integration tests for CORS configuration."""

    def test_cors_allows_requests(self, client: TestClient):
        """Test CORS allows requests."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Should not be blocked by CORS
        assert response.status_code in [200, 204]

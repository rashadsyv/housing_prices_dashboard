"""Integration tests for authentication API endpoints.

These tests require the full application stack including:
- Database connection
- FastAPI application
- All middleware
"""

from fastapi.testclient import TestClient


class TestAPIKeyCreationAPI:
    """Integration tests for API key creation endpoints."""

    def test_create_api_key_success(self, client: TestClient):
        """Test successful API key creation via API."""
        response = client.post(
            "/auth/keys",
            json={"name": "My Test Key", "description": "A test API key"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Test Key"
        assert "key" in data
        assert len(data["key"]) == 64  # 32 bytes hex = 64 chars
        assert data["is_active"] is True

    def test_create_api_key_without_description(self, client: TestClient):
        """Test API key creation without description via API."""
        response = client.post("/auth/keys", json={"name": "Simple Key"})

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Simple Key"

    def test_create_api_key_empty_name_fails(self, client: TestClient):
        """Test API key creation with empty name fails via API."""
        response = client.post("/auth/keys", json={"name": ""})
        assert response.status_code == 422  # Validation error

    def test_create_api_key_missing_name_fails(self, client: TestClient):
        """Test API key creation without name fails via API."""
        response = client.post("/auth/keys", json={})
        assert response.status_code == 422


class TestTokenGenerationAPI:
    """Integration tests for token generation endpoints."""

    def test_get_token_success(self, client: TestClient, api_key: str):
        """Test successful token generation via API."""
        response = client.post("/auth/token", json={"api_key": api_key})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_get_token_invalid_key(self, client: TestClient):
        """Test token generation with invalid API key via API."""
        response = client.post("/auth/token", json={"api_key": "invalid-key"})

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid API key"

    def test_get_token_empty_key(self, client: TestClient):
        """Test token generation with empty API key via API."""
        response = client.post("/auth/token", json={"api_key": ""})
        assert response.status_code == 422


class TestAPIKeyManagementAPI:
    """Integration tests for API key management endpoints."""

    def test_list_api_keys(self, client: TestClient, auth_headers: dict):
        """Test listing API keys requires authentication."""
        response = client.get("/auth/keys", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the key we created

    def test_list_api_keys_unauthorized(self, client: TestClient):
        """Test listing API keys without auth fails."""
        response = client.get("/auth/keys")
        assert response.status_code == 403  # No authorization header

    def test_deactivate_api_key(self, client: TestClient, auth_headers: dict):
        """Test deactivating an API key via API."""
        # First create another key to deactivate
        create_response = client.post("/auth/keys", json={"name": "Key to deactivate"})
        key_id = create_response.json()["id"]

        # Deactivate it
        response = client.delete(f"/auth/keys/{key_id}", headers=auth_headers)

        assert response.status_code == 200
        assert "deactivated" in response.json()["message"].lower()

    def test_deactivate_nonexistent_key(self, client: TestClient, auth_headers: dict):
        """Test deactivating a non-existent API key via API."""
        response = client.delete("/auth/keys/99999", headers=auth_headers)
        assert response.status_code == 404


class TestTokenValidationAPI:
    """Integration tests for token validation."""

    def test_invalid_token_rejected(self, client: TestClient):
        """Test invalid token is rejected by API."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/auth/keys", headers=headers)
        assert response.status_code == 401

    def test_malformed_auth_header_rejected(self, client: TestClient):
        """Test malformed authorization header is rejected by API."""
        headers = {"Authorization": "NotBearer token"}
        response = client.get("/auth/keys", headers=headers)
        assert response.status_code == 403


class TestFullAuthFlow:
    """Integration tests for complete authentication flow."""

    def test_full_auth_flow(self, client: TestClient):
        """Test complete authentication flow: create key -> get token -> use token."""
        # Step 1: Create API key
        create_response = client.post(
            "/auth/keys",
            json={"name": "Flow Test Key", "description": "Testing full flow"},
        )
        assert create_response.status_code == 201
        api_key = create_response.json()["key"]

        # Step 2: Exchange API key for token
        token_response = client.post("/auth/token", json={"api_key": api_key})
        assert token_response.status_code == 200
        token = token_response.json()["access_token"]

        # Step 3: Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        protected_response = client.get("/auth/keys", headers=headers)
        assert protected_response.status_code == 200

        # Step 4: Verify our key is in the list
        keys = protected_response.json()
        assert any(k["name"] == "Flow Test Key" for k in keys)

"""Unit tests for security functions - no database required."""

from datetime import timedelta

from jose import jwt

from src.config import settings
from src.core.security import (
    create_access_token,
    decode_access_token,
    generate_api_key,
    hash_password,
    verify_password,
)


class TestJWTTokens:
    """Test JWT token creation and decoding."""

    def test_create_access_token(self):
        """Test creating access token with subject."""
        token = create_access_token(data={"sub": "test-key-id"})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_custom_expiry(self):
        """Test creating token with custom expiry."""
        token = create_access_token(
            data={"sub": "test-key-id"},
            expires_delta=timedelta(hours=2),
        )
        assert token is not None

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        subject = "test-key-123"
        token = create_access_token(data={"sub": subject})

        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == subject

    def test_decode_invalid_token(self):
        """Test decoding an invalid token returns None."""
        decoded = decode_access_token("invalid-token")
        assert decoded is None

    def test_decode_malformed_token(self):
        """Test decoding a malformed token returns None."""
        decoded = decode_access_token("not.a.valid.jwt.token")
        assert decoded is None

    def test_token_contains_expiry(self):
        """Test token contains expiry claim."""
        token = create_access_token(data={"sub": "test"})
        decoded = decode_access_token(token)
        assert "exp" in decoded

    def test_token_algorithm(self):
        """Test token uses correct algorithm."""
        token = create_access_token(data={"sub": "test"})
        # Decode without verification to check header
        header = jwt.get_unverified_header(token)
        assert header["alg"] == settings.ALGORITHM


class TestPasswordHashing:
    """Test password/API key hashing and verification."""

    def test_hash_password(self):
        """Test hashing a password/API key."""
        api_key = "test-api-key-12345"
        hashed = hash_password(api_key)

        assert hashed is not None
        assert hashed != api_key  # Should not be plaintext
        assert len(hashed) > 0

    def test_hash_same_key_different_results(self):
        """Test hashing same key produces different hashes (due to salt)."""
        api_key = "test-api-key-12345"
        hash1 = hash_password(api_key)
        hash2 = hash_password(api_key)

        # bcrypt uses random salt, so hashes should differ
        assert hash1 != hash2

    def test_verify_correct_password(self):
        """Test verifying correct password/API key."""
        api_key = "test-api-key-12345"
        hashed = hash_password(api_key)

        assert verify_password(api_key, hashed) is True

    def test_verify_wrong_password(self):
        """Test verifying wrong password/API key fails."""
        api_key = "test-api-key-12345"
        hashed = hash_password(api_key)

        assert verify_password("wrong-key", hashed) is False

    def test_verify_empty_password(self):
        """Test verifying empty password fails gracefully."""
        hashed = hash_password("some-key")
        # Empty string should not match
        assert verify_password("", hashed) is False


class TestAPIKeyGeneration:
    """Test API key generation."""

    def test_generate_api_key_length(self):
        """Test generated API key has correct length."""
        key = generate_api_key()
        # 32 bytes = 64 hex characters
        assert len(key) == 64

    def test_generate_api_key_unique(self):
        """Test generated API keys are unique."""
        keys = [generate_api_key() for _ in range(100)]
        assert len(set(keys)) == 100  # All unique

    def test_generate_api_key_hex(self):
        """Test generated API key is valid hex."""
        key = generate_api_key()
        # Should be valid hex string
        int(key, 16)  # Will raise if not valid hex

    def test_generate_api_key_lowercase(self):
        """Test generated API key is lowercase hex."""
        key = generate_api_key()
        assert key == key.lower()

"""Authentication service for token generation and validation."""

from datetime import timedelta

from src.auth.repository import AuthRepository
from src.auth.schema import APIKeyCreate, APIKeyResponse, TokenResponse
from src.config import settings
from src.core.security import create_access_token
from src.models import APIKey


class AuthService:
    """Service for authentication operations."""

    def __init__(self, repo: AuthRepository) -> None:
        self.repo = repo

    def create_api_key(self, data: APIKeyCreate) -> APIKeyResponse:
        """Create a new API key and return it (plain key only returned once)."""
        api_key, plain_key = self.repo.create_api_key(
            name=data.name, description=data.description
        )
        return APIKeyResponse(
            id=api_key.id,
            name=api_key.name,
            key=plain_key,
            created_at=api_key.created_at,
            is_active=api_key.is_active,
        )

    def generate_token(self, api_key: str) -> TokenResponse | None:
        """Generate a JWT token for a valid API key."""
        key_record = self.repo.validate_key(api_key)
        if not key_record:
            return None

        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(key_record.id), "name": key_record.name},
            expires_delta=expires_delta,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def validate_api_key(self, api_key: str) -> APIKey | None:
        """Validate an API key and return the record if valid."""
        return self.repo.validate_key(api_key)

    def get_all_keys(self, skip: int = 0, limit: int = 100) -> list[APIKey]:
        return self.repo.get_all(skip=skip, limit=limit)

    def deactivate_key(self, key_id: int) -> bool:
        return self.repo.deactivate(key_id)

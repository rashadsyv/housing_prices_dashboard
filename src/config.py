"""Application configuration using Pydantic Settings."""

import logging
import os
from typing import Any, Literal

from fastapi.security import HTTPBearer
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    ENVIRONMENT: Literal["development", "production", "testing"] = os.getenv(
        "ENVIRONMENT", "development"
    )
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = os.getenv(
        "LOG_LEVEL", "INFO"
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))

    # API Settings
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Housing Price Prediction API")
    VERSION: str = os.getenv("VERSION", "1.0.0")

    # ML Model
    MODEL_PATH: str = os.getenv("MODEL_PATH", "model.joblib")

    # CORS
    CORS_ALLOWED_ORIGINS: str = os.getenv("CORS_ALLOWED_ORIGINS", "*")

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=f".env.{os.environ.get('ENVIRONMENT')}"
        if os.environ.get("ENVIRONMENT")
        else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"

    @property
    def cors_origins(self) -> list[str]:
        if self.CORS_ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",")]


settings = Config()

http_bearer = HTTPBearer(
    scheme_name="HTTPBearer",
    description="Enter your JWT token (obtained from /auth/token endpoint)",
    auto_error=True,
)

optional_http_bearer = HTTPBearer(
    scheme_name="Bearer Token (Optional)",
    description="Optional JWT token",
    auto_error=False,
)

fastapi_app_config: dict[str, Any] = {
    "title": settings.PROJECT_NAME,
    "description": """
## Housing Price Prediction API

This API provides house price predictions based on California housing data.

### Quick Start

1. Create an API key via `POST /auth/keys`
2. Get a token via `POST /auth/token` using your API key
3. Make predictions via `POST /predict` with your token

### Authentication

All prediction endpoints require a Bearer token:

```
Authorization: Bearer <your_token>
```
""",
    "version": settings.VERSION,
    "docs_url": "/docs" if settings.is_development else None,
    "redoc_url": "/redoc" if settings.is_development else None,
    "openapi_tags": [
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "Authentication", "description": "API key and token management"},
        {"name": "Predictions", "description": "House price predictions"},
        {"name": "Prediction Logs", "description": "Prediction audit trail"},
    ],
}

logger = logging.getLogger(__name__)


def get_settings() -> Config:
    """Get settings instance."""
    return settings

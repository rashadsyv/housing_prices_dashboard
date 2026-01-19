"""Health check API routes."""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from sqlalchemy import text

from src.config import settings
from src.core.database import engine
from src.ml.model import load_model

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    timestamp: datetime
    version: str
    environment: str


class DetailedHealthResponse(HealthResponse):
    components: dict[str, str] = Field(
        ..., examples=[{"database": "healthy", "model": "healthy"}]
    )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC),
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )


@router.get(
    "/health/detailed",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
)
async def detailed_health_check() -> DetailedHealthResponse:
    """Check all components: database and ML model."""
    components = {}

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        components["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        components["database"] = "unhealthy"

    try:
        load_model()
        components["model"] = "healthy"
    except Exception as e:
        logger.error(f"Model health check failed: {e}")
        components["model"] = "unhealthy"

    overall_status = (
        "healthy" if all(v == "healthy" for v in components.values()) else "degraded"
    )

    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.now(UTC),
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        components=components,
    )

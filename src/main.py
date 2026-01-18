"""Housing Price Prediction API - FastAPI application entry point."""

import logging
import time
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.openapi.utils import get_openapi
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.auth.router import router as auth_router
from src.config import fastapi_app_config, settings
from src.core.database import init_db
from src.core.logging import setup_logging
from src.core.rate_limiter import limiter
from src.health.router import router as health_router
from src.logs.router import router as logs_router
from src.predictions.router import router as predictions_router
from src.predictions.service import load_model

logger = logging.getLogger(__name__)


async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown handler."""
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    if settings.is_development:
        logger.info("Development mode: Auto-creating database tables...")
        init_db()
        logger.info("Database tables created")
    else:
        logger.info("Production mode: Run 'alembic upgrade head' for migrations")

    logger.info("Loading ML model...")
    try:
        load_model()
        logger.info("ML model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")
        raise

    yield

    logger.info("Shutting down application...")


app = FastAPI(lifespan=lifespan, **fastapi_app_config)


def custom_openapi() -> Any:
    """Generate custom OpenAPI schema with security schemes."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token obtained from /auth/token",
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore [method-assign]

# Rate limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next: Any) -> Any:
    """Log requests and add correlation IDs for tracing."""
    correlation_id = str(uuid.uuid4())[:8]
    request.state.correlation_id = correlation_id

    start_time = time.time()
    logger.info(f"[{correlation_id}] {request.method} {request.url.path} - Started")

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"[{correlation_id}] Request failed: {e}")
        raise

    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        f"[{correlation_id}] {request.method} {request.url.path} "
        f"→ {response.status_code} ({duration_ms:.0f}ms)"
    )

    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time"] = f"{duration_ms:.0f}ms"

    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with correlation ID."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.warning(f"[{correlation_id}] HTTP {exc.status_code}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "correlation_id": correlation_id},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.warning(f"[{correlation_id}] Validation error: {exc.errors()}")

    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field_path}: {error.get('msg', '')}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors,
            "correlation_id": correlation_id,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.error(f"[{correlation_id}] Unhandled error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "correlation_id": correlation_id},
    )


# Register routers
app.include_router(health_router, tags=["Health"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(predictions_router, prefix="/predict", tags=["Predictions"])
app.include_router(logs_router, prefix="/logs", tags=["Prediction Logs"])


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }

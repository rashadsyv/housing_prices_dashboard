"""Authentication API routes."""

import logging

from fastapi import APIRouter, HTTPException, Request, status

from src.auth.dependencies import AuthServiceDep, CurrentUserDep
from src.auth.schema import (
    APIKeyCreate,
    APIKeyInfo,
    APIKeyResponse,
    MessageResponse,
    TokenRequest,
    TokenResponse,
)
from src.core.rate_limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/keys",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API Key",
    description="Create a new API key. The key is only returned once - store it securely!",
)
@limiter.limit("10/hour")
async def create_api_key(
    request: Request,
    data: APIKeyCreate,
    service: AuthServiceDep,
) -> APIKeyResponse:
    logger.info(f"Creating new API key: {data.name}")
    api_key = service.create_api_key(data)
    logger.info(f"API key created: id={api_key.id}")
    return api_key


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Get Access Token",
    description="Exchange your API key for a JWT access token.",
)
@limiter.limit("30/minute")
async def get_token(
    request: Request,
    data: TokenRequest,
    service: AuthServiceDep,
) -> TokenResponse:
    token = service.generate_token(data.api_key)
    if token is None:
        logger.warning("Invalid API key used for token request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    logger.info("Token generated successfully")
    return token


@router.get(
    "/keys",
    response_model=list[APIKeyInfo],
    summary="List API Keys",
    description="List all API keys (requires authentication).",
)
async def list_api_keys(
    current_user: CurrentUserDep,
    service: AuthServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> list[APIKeyInfo]:
    keys = service.get_all_keys(skip=skip, limit=limit)
    return [
        APIKeyInfo(
            id=key.id,
            name=key.name,
            description=key.description,
            created_at=key.created_at,
            updated_at=key.updated_at,
            is_active=key.is_active,
            is_deleted=key.is_deleted,
        )
        for key in keys
    ]


@router.delete(
    "/keys/{key_id}",
    response_model=MessageResponse,
    summary="Deactivate API Key",
    description="Deactivate an API key (requires authentication).",
)
async def deactivate_api_key(
    key_id: int,
    current_user: CurrentUserDep,
    service: AuthServiceDep,
) -> MessageResponse:
    logger.info(f"Deactivating API key {key_id}")
    if not service.deactivate_key(key_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )
    return MessageResponse(message="API key deactivated successfully")

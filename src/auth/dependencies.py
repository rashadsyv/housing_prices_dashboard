"""Authentication dependencies for FastAPI."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.auth.repository import AuthRepository
from src.auth.service import AuthService
from src.config import http_bearer
from src.core.database import get_db
from src.core.security import decode_access_token

DbSessionDep = Annotated[Session, Depends(get_db)]


def get_auth_repo(session: DbSessionDep) -> AuthRepository:
    return AuthRepository(session)


AuthRepoDep = Annotated[AuthRepository, Depends(get_auth_repo)]


def get_auth_service(repo: AuthRepoDep) -> AuthService:
    return AuthService(repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    repo: AuthRepoDep,
) -> dict:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    key_id = payload.get("sub")
    if key_id is None:
        raise credentials_exception

    api_key = repo.get_by_id(int(key_id))
    if api_key is None or not api_key.is_active or api_key.is_deleted:
        raise credentials_exception

    return {"id": api_key.id, "name": api_key.name}


CurrentUserDep = Annotated[dict, Depends(get_current_user)]

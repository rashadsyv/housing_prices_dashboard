"""Pydantic schemas for authentication."""

from datetime import datetime

from pydantic import BaseModel, Field


class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["My Application"])
    description: str | None = Field(default=None, max_length=500)


class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str  # Only returned once on creation
    created_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}


class APIKeyInfo(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_deleted: bool

    model_config = {"from_attributes": True}


class TokenRequest(BaseModel):
    api_key: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    message: str

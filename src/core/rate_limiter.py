"""Rate limiting configuration using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import settings

limiter = Limiter(key_func=get_remote_address)


def get_rate_limit_string() -> str:
    """Get the rate limit string (e.g., '100/minute')."""
    return f"{settings.RATE_LIMIT_PER_MINUTE}/minute"

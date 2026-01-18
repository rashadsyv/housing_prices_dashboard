"""Repository for API key database operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.security import generate_api_key, hash_password, verify_password
from src.models import APIKey


class AuthRepository:
    """Repository for API key CRUD operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_api_key(
        self, name: str, description: str | None = None
    ) -> tuple[APIKey, str]:
        """Create a new API key. Returns (APIKey, plain_key) - plain key only returned once!"""
        plain_key = generate_api_key()
        key_hash = hash_password(plain_key)

        api_key = APIKey(
            name=name,
            description=description,
            key_hash=key_hash,
            key_prefix=plain_key[:8],
        )

        self.session.add(api_key)
        self.session.commit()
        self.session.refresh(api_key)

        return api_key, plain_key

    def get_by_id(self, key_id: int) -> APIKey | None:
        stmt = select(APIKey).where(APIKey.id == key_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_all(
        self, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> list[APIKey]:
        stmt = select(APIKey)
        if not include_deleted:
            stmt = stmt.where(APIKey.deleted_at == None)  # noqa: E711
        stmt = stmt.offset(skip).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def validate_key(self, plain_key: str) -> APIKey | None:
        """Validate an API key and return the record if valid."""
        key_prefix = plain_key[:8]
        stmt = select(APIKey).where(
            APIKey.key_prefix == key_prefix,
            APIKey.is_active == True,  # noqa: E712
            APIKey.deleted_at == None,  # noqa: E711
        )
        candidates = self.session.execute(stmt).scalars().all()

        for candidate in candidates:
            if verify_password(plain_key, candidate.key_hash):
                return candidate
        return None

    def deactivate(self, key_id: int) -> bool:
        api_key = self.get_by_id(key_id)
        if api_key:
            api_key.is_active = False
            self.session.commit()
            return True
        return False

    def delete(self, key_id: int, hard_delete: bool = False) -> bool:
        api_key = self.get_by_id(key_id)
        if api_key:
            if hard_delete:
                self.session.delete(api_key)
            else:
                api_key.soft_delete()
            self.session.commit()
            return True
        return False

    def restore(self, key_id: int) -> bool:
        api_key = self.get_by_id(key_id)
        if api_key and api_key.is_deleted:
            api_key.restore()
            self.session.commit()
            return True
        return False

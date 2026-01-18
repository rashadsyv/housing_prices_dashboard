"""Common SQLAlchemy types and mixins for database models."""

import uuid
from datetime import UTC, datetime
from typing import Annotated, Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

# Primary key types
IntPK = Annotated[
    int,
    mapped_column(Integer, primary_key=True, index=True, autoincrement=True),
]

StringPK = Annotated[
    str,
    mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
]

# Timestamp types
CreatedAt = Annotated[
    datetime,
    mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False),
]

UpdatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    ),
]

DeletedAt = Annotated[
    datetime | None,
    mapped_column(DateTime, nullable=True, default=None),
]


class CascadingForeignKey(ForeignKey):
    """ForeignKey with CASCADE on delete and update."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("ondelete", "CASCADE")
        kwargs.setdefault("onupdate", "CASCADE")
        super().__init__(*args, **kwargs)


class TimestampMixin:
    """Mixin that adds created_at and updated_at fields."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class TimestampWithDeleteMixin(TimestampMixin):
    """Mixin with timestamps and soft delete support."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        self.deleted_at = None


class MetadataMixin:
    """Mixin that adds a JSON metadata field for flexible data storage."""

    meta: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, default=None
    )

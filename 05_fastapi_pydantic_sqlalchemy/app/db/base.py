"""SQLAlchemy 2.0 Declarative Base and Shared Mixins."""

from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Modern SQLAlchemy 2.0 Declarative Base class.
    
    Subclasses use Mapped[T] annotations and mapped_column() descriptors.
    """
    pass


class TimestampMixin:
    """Reusable mixin providing created_at and updated_at audit timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

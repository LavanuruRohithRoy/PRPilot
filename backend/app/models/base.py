from sqlalchemy.orm import DeclarativeBase, Mapped

from app.core.types import TimestampMixin, UUIDPrimaryKey


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


class BaseModel(Base, TimestampMixin):
    """Abstract base model that includes UUID primary key and timestamps."""

    __abstract__ = True

    id: Mapped[UUIDPrimaryKey]

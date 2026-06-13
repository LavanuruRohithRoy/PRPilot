import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RepositoryBase(BaseModel):
    """Base schema for Repository fields."""

    owner: str
    name: str
    full_name: str
    is_active: bool = True


class RepositoryCreate(RepositoryBase):
    """Schema for creating a Repository."""

    pass


class RepositoryUpdate(BaseModel):
    """Schema for updating a Repository."""

    owner: str | None = None
    name: str | None = None
    full_name: str | None = None
    is_active: bool | None = None


class Repository(RepositoryBase):
    """Schema representing a Repository with database metadata."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

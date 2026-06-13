import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import PullRequestStatus


class PullRequestBase(BaseModel):
    """Base schema for PullRequest fields."""

    repository_id: uuid.UUID
    pr_number: int
    title: str
    author: str
    status: PullRequestStatus = PullRequestStatus.OPEN
    opened_at: datetime
    closed_at: datetime | None = None


class PullRequestCreate(PullRequestBase):
    """Schema for creating a PullRequest."""

    pass


class PullRequestUpdate(BaseModel):
    """Schema for updating a PullRequest."""

    repository_id: uuid.UUID | None = None
    pr_number: int | None = None
    title: str | None = None
    author: str | None = None
    status: PullRequestStatus | None = None
    opened_at: datetime | None = None
    closed_at: datetime | None = None


class PullRequest(PullRequestBase):
    """Schema representing a PullRequest with database metadata."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

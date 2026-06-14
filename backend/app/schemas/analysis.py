import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AnalysisStatus, RiskLevel


class AnalysisBase(BaseModel):
    """Base schema for Analysis fields."""

    pull_request_id: uuid.UUID
    status: AnalysisStatus = AnalysisStatus.PENDING
    summary: str | None = None
    risk_score: int | None = Field(default=None, ge=0, le=100)
    risk_level: RiskLevel | None = None
    findings: list[str] | None = None


class AnalysisCreate(AnalysisBase):
    """Schema for creating an Analysis."""

    pass


class AnalysisUpdate(BaseModel):
    """Schema for updating an Analysis."""

    pull_request_id: uuid.UUID | None = None
    status: AnalysisStatus | None = None
    summary: str | None = None
    risk_score: int | None = Field(default=None, ge=0, le=100)
    risk_level: RiskLevel | None = None
    findings: list[str] | None = None


class Analysis(AnalysisBase):
    """Schema representing an Analysis with database metadata."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

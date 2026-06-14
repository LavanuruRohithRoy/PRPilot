import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import AnalysisStatus, RiskLevel


class DashboardRecentAnalysis(BaseModel):
    """Schema representing details of a recent pull request analysis run."""

    id: uuid.UUID
    pull_request_id: uuid.UUID
    pr_title: str
    pr_number: int
    repository_name: str
    risk_score: int | None
    risk_level: RiskLevel | None
    status: AnalysisStatus
    created_at: datetime


class DashboardSummary(BaseModel):
    """Schema representing aggregated metrics and recent runs for the system
    overview.
    """

    repositories: int
    pull_requests: int
    analyses: int
    high_risk: int
    medium_risk: int
    low_risk: int
    recent_analyses: list[DashboardRecentAnalysis]

"""PRPilot data validation and serialization schemas package."""

from app.schemas.analysis import (
    Analysis,
    AnalysisBase,
    AnalysisCreate,
    AnalysisUpdate,
)
from app.schemas.dashboard import DashboardRecentAnalysis, DashboardSummary
from app.schemas.errors import ErrorResponse
from app.schemas.intelligence import GroundedCitation, GroundedQueryResponse
from app.schemas.pull_request import (
    PullRequest,
    PullRequestBase,
    PullRequestCreate,
    PullRequestUpdate,
)
from app.schemas.repository import (
    Repository,
    RepositoryBase,
    RepositoryCreate,
    RepositoryUpdate,
)

__all__ = [
    "Analysis",
    "AnalysisBase",
    "AnalysisCreate",
    "AnalysisUpdate",
    "DashboardRecentAnalysis",
    "DashboardSummary",
    "ErrorResponse",
    "GroundedCitation",
    "GroundedQueryResponse",
    "PullRequest",
    "PullRequestBase",
    "PullRequestCreate",
    "PullRequestUpdate",
    "Repository",
    "RepositoryBase",
    "RepositoryCreate",
    "RepositoryUpdate",
]

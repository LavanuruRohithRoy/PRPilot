from app.models.pull_request import PullRequest
from app.repositories.base import BaseRepository


class PullRequestRepository(BaseRepository[PullRequest]):
    """Repository interface for the PullRequest domain model."""

    pass

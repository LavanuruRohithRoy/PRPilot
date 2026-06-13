import uuid
from abc import ABC, abstractmethod

from app.models.pull_request import PullRequest
from app.models.repository import Repository


class RepoSyncService(ABC):
    """Abstract service interface for syncing repository data from VCS providers."""

    @abstractmethod
    async def sync_repository(self, owner: str, name: str) -> Repository:
        """Sync a repository by owner and name from a VCS provider."""
        pass

    @abstractmethod
    async def sync_pull_request(
        self, repo_id: uuid.UUID, pr_number: int
    ) -> PullRequest:
        """Sync a pull request from a VCS provider to the local database."""
        pass

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainValidationError, EntityNotFoundError, PRPilotError
from app.integrations.github.client import GitHubClient
from app.integrations.github.exceptions import (
    GitHubAuthenticationError,
    GitHubRateLimitError,
    GitHubRequestError,
)
from app.integrations.github.mappers import map_pull_request, map_repository
from app.integrations.github.schemas import GitHubPullRequest, GitHubRepository
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.repositories.pull_request import PullRequestRepository
from app.repositories.repository import RepositoryRepository
from app.services.repo_sync import RepoSyncService


class GitHubSyncService(RepoSyncService):
    """Concrete service implementing RepoSyncService for GitHub synchronization."""

    def __init__(
        self,
        client: GitHubClient,
        repository_repo: RepositoryRepository,
        pull_request_repo: PullRequestRepository,
        session: AsyncSession,
    ) -> None:
        self.client = client
        self.repository_repo = repository_repo
        self.pull_request_repo = pull_request_repo
        self.session = session

    def _handle_exception(self, e: Exception) -> Exception:
        """Translate integration/network exceptions into core application exceptions."""
        if isinstance(e, GitHubAuthenticationError):
            return DomainValidationError("GitHub authorization failed.")
        elif isinstance(e, GitHubRateLimitError):
            return PRPilotError("GitHub API rate limit exceeded.")
        elif isinstance(e, GitHubRequestError):
            return PRPilotError(f"GitHub request failed: {e!s}")
        return e

    async def sync_repository(self, owner: str, name: str) -> Repository:
        """Sync a repository by owner and name from GitHub to the database."""
        try:
            response = await self.client.get(f"repos/{owner}/{name}")
            dto = GitHubRepository.model_validate(response)
            repo_attrs = map_repository(dto)

            repo = await self.repository_repo.get_by_full_name(repo_attrs["full_name"])
            if repo:
                repo = await self.repository_repo.update(repo, **repo_attrs)
            else:
                repo = await self.repository_repo.create(**repo_attrs)

            await self.session.commit()
            await self.session.refresh(repo)
            return repo
        except Exception as e:
            await self.session.rollback()
            raise self._handle_exception(e) from e

    async def sync_pull_request(
        self, repo_id: uuid.UUID, pr_number: int
    ) -> PullRequest:
        """Sync a pull request from GitHub to the database."""
        try:
            repo = await self.repository_repo.get_by_id(repo_id)
            if not repo:
                raise EntityNotFoundError(f"Repository with ID {repo_id} not found.")

            response = await self.client.get(
                f"repos/{repo.owner}/{repo.name}/pulls/{pr_number}"
            )
            dto = GitHubPullRequest.model_validate(response)
            pr_attrs = map_pull_request(dto)

            pr = await self.pull_request_repo.get_by_repository_and_number(
                repo_id, pr_number
            )
            if pr:
                pr = await self.pull_request_repo.update(pr, **pr_attrs)
            else:
                pr = await self.pull_request_repo.create(
                    repository_id=repo_id, **pr_attrs
                )

            await self.session.commit()
            await self.session.refresh(pr)
            return pr
        except Exception as e:
            await self.session.rollback()
            raise self._handle_exception(e) from e

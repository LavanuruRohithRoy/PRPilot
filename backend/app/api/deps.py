from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.integrations.github.client import GitHubClient
from app.integrations.github.services import GitHubSyncService
from app.repositories.analysis import AnalysisRepository
from app.repositories.pull_request import PullRequestRepository
from app.repositories.repository import RepositoryRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider yielding active database sessions."""
    async for session in get_session():
        yield session


def get_repository_repository(
    session: AsyncSession = Depends(get_db_session),
) -> RepositoryRepository:
    """Dependency provider for RepositoryRepository."""
    return RepositoryRepository(session)


def get_pull_request_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PullRequestRepository:
    """Dependency provider for PullRequestRepository."""
    return PullRequestRepository(session)


def get_analysis_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AnalysisRepository:
    """Dependency provider for AnalysisRepository."""
    return AnalysisRepository(session)


def get_github_client() -> GitHubClient:
    """Dependency provider for GitHubClient."""
    return GitHubClient()


def get_github_sync_service(
    client: GitHubClient = Depends(get_github_client),
    repo_repo: RepositoryRepository = Depends(get_repository_repository),
    pr_repo: PullRequestRepository = Depends(get_pull_request_repository),
    session: AsyncSession = Depends(get_db_session),
) -> GitHubSyncService:
    """Dependency provider for GitHubSyncService."""
    return GitHubSyncService(
        client=client,
        repository_repo=repo_repo,
        pull_request_repo=pr_repo,
        session=session,
    )

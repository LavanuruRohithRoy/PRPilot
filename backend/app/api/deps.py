from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.integrations.github.client import GitHubClient
from app.integrations.github.services import GitHubSyncService
from app.repositories.analysis import AnalysisRepository
from app.repositories.pull_request import PullRequestRepository
from app.repositories.repository import RepositoryRepository
from app.services.analysis_engine import AnalysisEngine
from app.services.analysis_service import AnalysisService
from app.services.dashboard_service import DashboardService
from app.services.foundry_iq import FoundryIQService
from app.services.pr_analysis import PRAnalysisService


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


def get_analysis_engine() -> AnalysisEngine:
    """Dependency provider for AnalysisEngine."""
    return AnalysisEngine()


def get_analysis_service(
    repo: AnalysisRepository = Depends(get_analysis_repository),
    pr_repo: PullRequestRepository = Depends(get_pull_request_repository),
    session: AsyncSession = Depends(get_db_session),
    engine: AnalysisEngine = Depends(get_analysis_engine),
) -> PRAnalysisService:
    """Dependency provider for PRAnalysisService."""
    return AnalysisService(
        analysis_repo=repo,
        pull_request_repo=pr_repo,
        session=session,
        engine=engine,
    )


def get_dashboard_service(
    session: AsyncSession = Depends(get_db_session),
) -> DashboardService:
    """Dependency provider for DashboardService."""
    return DashboardService(session)


def get_foundry_iq_service(
    session: AsyncSession = Depends(get_db_session),
) -> FoundryIQService:
    """Dependency provider for FoundryIQService."""
    return FoundryIQService(session)

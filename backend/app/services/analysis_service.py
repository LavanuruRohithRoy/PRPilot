import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.models.analysis import Analysis
from app.repositories.analysis import AnalysisRepository
from app.repositories.pull_request import PullRequestRepository
from app.services.analysis_engine import AnalysisEngine
from app.services.pr_analysis import PRAnalysisService


class AnalysisService(PRAnalysisService):
    """Implementation of PRAnalysisService using deterministic AnalysisEngine."""

    def __init__(
        self,
        analysis_repo: AnalysisRepository,
        pull_request_repo: PullRequestRepository,
        session: AsyncSession,
        engine: AnalysisEngine,
    ) -> None:
        self.analysis_repo = analysis_repo
        self.pull_request_repo = pull_request_repo
        self.session = session
        self.engine = engine

    async def trigger_analysis(self, pr_id: uuid.UUID) -> Analysis:
        """Trigger deterministic analysis on a PR and store results."""
        pr = await self.pull_request_repo.get_by_id(pr_id)
        if not pr:
            raise EntityNotFoundError(f"Pull Request with ID {pr_id} not found.")

        # Execute analysis engine
        result = self.engine.analyze(pr)

        # Create new Analysis record
        analysis = await self.analysis_repo.create(
            pull_request_id=pr.id,
            status=result["status"],
            summary=result["summary"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            findings=result["findings"],
        )

        # Commit and refresh
        await self.session.commit()
        await self.session.refresh(analysis)

        return analysis

    async def get_analysis_status(self, analysis_id: uuid.UUID) -> Analysis:
        """Retrieve the status and results of a previously run analysis."""
        analysis = await self.analysis_repo.get_by_id(analysis_id)
        if not analysis:
            raise EntityNotFoundError(f"Analysis with ID {analysis_id} not found.")
        return analysis

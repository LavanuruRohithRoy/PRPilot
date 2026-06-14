from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.analysis import Analysis
from app.models.enums import RiskLevel
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.schemas.dashboard import DashboardRecentAnalysis, DashboardSummary


class DashboardService:
    """Service class executing consolidated queries to aggregate dashboard status
    metrics.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_dashboard_summary(self) -> DashboardSummary:
        """Query and return aggregated counts and recent analyses for the dashboard."""
        # 1. Total Repositories
        repo_count = await self.session.scalar(select(func.count(Repository.id))) or 0

        # 2. Total Pull Requests
        pr_count = await self.session.scalar(select(func.count(PullRequest.id))) or 0

        # 3. Consolidated Group-By for Analyses and Risk Levels
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        total_analyses = 0

        risk_query = select(Analysis.risk_level, func.count(Analysis.id)).group_by(
            Analysis.risk_level
        )
        risk_result = await self.session.execute(risk_query)

        for row in risk_result:
            level, count = row
            total_analyses += count
            if level == RiskLevel.HIGH:
                high_risk = count
            elif level == RiskLevel.MEDIUM:
                medium_risk = count
            elif level == RiskLevel.LOW:
                low_risk = count

        # 4. Fetch 5 Most Recent Analyses with PullRequest and Repository details
        recent_query = (
            select(Analysis)
            .options(
                joinedload(Analysis.pull_request).joinedload(PullRequest.repository)
            )
            .order_by(Analysis.created_at.desc())
            .limit(5)
        )
        recent_result = await self.session.execute(recent_query)
        analyses = recent_result.scalars().all()

        recent_analyses = [
            DashboardRecentAnalysis(
                id=a.id,
                pull_request_id=a.pull_request_id,
                pr_title=a.pull_request.title,
                pr_number=a.pull_request.pr_number,
                repository_name=a.pull_request.repository.full_name,
                risk_score=a.risk_score,
                risk_level=a.risk_level,
                status=a.status,
                created_at=a.created_at,
            )
            for a in analyses
        ]

        return DashboardSummary(
            repositories=repo_count,
            pull_requests=pr_count,
            analyses=total_analyses,
            high_risk=high_risk,
            medium_risk=medium_risk,
            low_risk=low_risk,
            recent_analyses=recent_analyses,
        )

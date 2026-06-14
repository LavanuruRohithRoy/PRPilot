import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select

from app.models.analysis import Analysis
from app.models.enums import AnalysisStatus, RiskLevel
from app.repositories.base import BaseRepository


class AnalysisRepository(BaseRepository[Analysis]):
    """Repository interface for the Analysis domain model."""

    async def get_by_id(self, id: uuid.UUID) -> Analysis | None:
        """Fetch a single Analysis by its primary key ID."""
        return await self.session.get(Analysis, id)

    async def create(
        self,
        pull_request_id: uuid.UUID,
        status: AnalysisStatus = AnalysisStatus.PENDING,
        summary: str | None = None,
        risk_score: int | None = None,
        risk_level: RiskLevel | None = None,
        findings: list[str] | None = None,
    ) -> Analysis:
        """Create and add a new Analysis entity to the current session."""
        analysis = Analysis(
            pull_request_id=pull_request_id,
            status=status,
            summary=summary,
            risk_score=risk_score,
            risk_level=risk_level,
            findings=findings,
        )
        self.session.add(analysis)
        return analysis

    async def update(self, analysis: Analysis, **kwargs: Any) -> Analysis:
        """Update fields on an existing Analysis entity."""
        for key, value in kwargs.items():
            if hasattr(analysis, key):
                setattr(analysis, key, value)
        return analysis

    async def get_latest_for_pull_request(self, pr_id: uuid.UUID) -> Analysis | None:
        """Fetch the latest Analysis for a pull request by created_at DESC."""
        query = (
            select(Analysis)
            .where(Analysis.pull_request_id == pr_id)
            .order_by(Analysis.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_pull_request(self, pr_id: uuid.UUID) -> Sequence[Analysis]:
        """Fetch all Analysis records for a pull request sorted by created_at DESC."""
        query = (
            select(Analysis)
            .where(Analysis.pull_request_id == pr_id)
            .order_by(Analysis.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_all(self) -> Sequence[Analysis]:
        """Fetch all Analysis records ordered by created_at DESC."""
        query = select(Analysis).order_by(Analysis.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

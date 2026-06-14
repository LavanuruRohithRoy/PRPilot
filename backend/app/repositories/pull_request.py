import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import select

from app.models.enums import PullRequestStatus
from app.models.pull_request import PullRequest
from app.repositories.base import BaseRepository


class PullRequestRepository(BaseRepository[PullRequest]):
    """Repository interface for the PullRequest domain model."""

    async def get_by_id(self, id: uuid.UUID) -> PullRequest | None:
        """Fetch a single PullRequest by its primary key ID."""
        return await self.session.get(PullRequest, id)

    async def get_by_repository_and_number(
        self, repo_id: uuid.UUID, pr_number: int
    ) -> PullRequest | None:
        """Fetch a single PullRequest by its parent repository ID and PR number."""
        query = select(PullRequest).where(
            PullRequest.repository_id == repo_id,
            PullRequest.pr_number == pr_number,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self,
        repository_id: uuid.UUID,
        pr_number: int,
        title: str,
        author: str,
        status: PullRequestStatus,
        opened_at: datetime,
        closed_at: datetime | None = None,
    ) -> PullRequest:
        """Create and add a new PullRequest entity to the current session."""
        pr = PullRequest(
            repository_id=repository_id,
            pr_number=pr_number,
            title=title,
            author=author,
            status=status,
            opened_at=opened_at,
            closed_at=closed_at,
        )
        self.session.add(pr)
        return pr

    async def update(self, pr: PullRequest, **kwargs: Any) -> PullRequest:
        """Update fields on an existing PullRequest entity."""
        for key, value in kwargs.items():
            if hasattr(pr, key):
                setattr(pr, key, value)
        return pr

    async def list_by_repository(self, repo_id: uuid.UUID) -> Sequence[PullRequest]:
        """Fetch all PullRequest records associated with a specific repository."""
        query = select(PullRequest).where(PullRequest.repository_id == repo_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_all(self) -> Sequence[PullRequest]:
        """Fetch all PullRequest records ordered by opened_at DESC."""
        query = select(PullRequest).order_by(PullRequest.opened_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

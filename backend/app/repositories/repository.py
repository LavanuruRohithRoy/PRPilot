import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select

from app.models.repository import Repository
from app.repositories.base import BaseRepository


class RepositoryRepository(BaseRepository[Repository]):
    """Repository interface for the Repository domain model."""

    async def get_by_id(self, id: uuid.UUID) -> Repository | None:
        """Fetch a single Repository by its primary key ID."""
        return await self.session.get(Repository, id)

    async def get_by_full_name(self, full_name: str) -> Repository | None:
        """Fetch a single Repository by its unique full_name."""
        query = select(Repository).where(Repository.full_name == full_name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self, owner: str, name: str, full_name: str, is_active: bool = True
    ) -> Repository:
        """Create and add a new Repository entity to the current session."""
        repo = Repository(
            owner=owner, name=name, full_name=full_name, is_active=is_active
        )
        self.session.add(repo)
        return repo

    async def update(self, repo: Repository, **kwargs: Any) -> Repository:
        """Update fields on an existing Repository entity."""
        for key, value in kwargs.items():
            if hasattr(repo, key):
                setattr(repo, key, value)
        return repo

    async def list_all(self) -> Sequence[Repository]:
        """Fetch all Repository records from the database."""
        query = select(Repository)
        result = await self.session.execute(query)
        return result.scalars().all()

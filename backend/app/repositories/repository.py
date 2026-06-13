from app.models.repository import Repository
from app.repositories.base import BaseRepository


class RepositoryRepository(BaseRepository[Repository]):
    """Repository interface for the Repository domain model."""

    pass

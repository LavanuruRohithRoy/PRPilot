from app.models.analysis import Analysis
from app.repositories.base import BaseRepository


class AnalysisRepository(BaseRepository[Analysis]):
    """Repository interface for the Analysis domain model."""

    pass

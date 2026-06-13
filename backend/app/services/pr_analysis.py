import uuid
from abc import ABC, abstractmethod

from app.models.analysis import Analysis


class PRAnalysisService(ABC):
    """Abstract service interface for triggering and checking PR analyses."""

    @abstractmethod
    async def trigger_analysis(self, pr_id: uuid.UUID) -> Analysis:
        """Trigger a new AI analysis for a pull request."""
        pass

    @abstractmethod
    async def get_analysis_status(self, analysis_id: uuid.UUID) -> Analysis:
        """Get the status of an AI analysis."""
        pass

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_dashboard_service
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get(
    "",
    response_model=DashboardSummary,
    responses={
        200: {
            "description": "Dashboard overview aggregated metrics.",
            "content": {
                "application/json": {
                    "example": {
                        "repositories": 4,
                        "pull_requests": 17,
                        "analyses": 17,
                        "high_risk": 3,
                        "medium_risk": 9,
                        "low_risk": 5,
                        "recent_analyses": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "pull_request_id": (
                                    "987f6543-e21b-34d5-c678-826614174111"
                                ),
                                "pr_title": "PR marked as WIP",
                                "pr_number": 42,
                                "repository_name": "owner/repo",
                                "risk_score": 75,
                                "risk_level": "HIGH",
                                "status": "completed",
                                "created_at": "2026-06-14T12:00:00Z",
                            }
                        ],
                    }
                }
            },
        }
    },
)
async def get_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """Fetch aggregated system metrics and recent analysis runs for the dashboard."""
    return await service.get_dashboard_summary()

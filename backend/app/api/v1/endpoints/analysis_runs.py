import uuid
from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_analysis_service
from app.schemas.analysis import Analysis as AnalysisSchema
from app.services.pr_analysis import PRAnalysisService

router = APIRouter()


@router.post(
    "/run/{pr_id}",
    response_model=AnalysisSchema,
    responses={
        200: {
            "description": "Analysis run completed successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "pull_request_id": "987f6543-e21b-34d5-c678-826614174111",
                        "status": "completed",
                        "summary": (
                            "Analysis completed with risk level HIGH (Score: 55/100).\n"
                            "Findings:\n"
                            "- PR is marked as Work In Progress (WIP) or Draft\n"
                            "- PR title is extremely short"
                        ),
                        "risk_score": 55,
                        "risk_level": "MEDIUM",
                        "findings": [
                            "PR is marked as Work In Progress (WIP) or Draft",
                            "PR title is extremely short",
                        ],
                        "created_at": "2026-06-14T12:00:00Z",
                        "updated_at": "2026-06-14T12:00:00Z",
                    }
                }
            },
        }
    },
)
async def trigger_pr_analysis(
    pr_id: uuid.UUID,
    analysis_service: PRAnalysisService = Depends(get_analysis_service),
) -> Any:
    """Trigger a deterministic rule-based analysis run against a PR."""
    return await analysis_service.trigger_analysis(pr_id)


@router.get(
    "/{analysis_id}",
    response_model=AnalysisSchema,
    responses={
        200: {
            "description": "Stored analysis retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "pull_request_id": "987f6543-e21b-34d5-c678-826614174111",
                        "status": "completed",
                        "summary": (
                            "Analysis completed with risk level LOW (Score: 15/100).\n"
                            "Findings:\n"
                            "- PR title is extremely short"
                        ),
                        "risk_score": 15,
                        "risk_level": "LOW",
                        "findings": ["PR title is extremely short"],
                        "created_at": "2026-06-14T12:00:00Z",
                        "updated_at": "2026-06-14T12:00:00Z",
                    }
                }
            },
        }
    },
)
async def get_analysis_status(
    analysis_id: uuid.UUID,
    analysis_service: PRAnalysisService = Depends(get_analysis_service),
) -> Any:
    """Retrieve status and results of a previously executed pull request analysis."""
    return await analysis_service.get_analysis_status(analysis_id)

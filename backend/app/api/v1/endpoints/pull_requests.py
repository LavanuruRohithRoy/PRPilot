import uuid
from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_analysis_repository, get_pull_request_repository
from app.core.exceptions import EntityNotFoundError
from app.repositories.analysis import AnalysisRepository
from app.repositories.pull_request import PullRequestRepository
from app.schemas.analysis import Analysis as AnalysisSchema
from app.schemas.pull_request import PullRequest as PullRequestSchema

router = APIRouter()


@router.get("/{id}", response_model=PullRequestSchema, tags=["pull-requests"])
async def get_pull_request(
    id: uuid.UUID,
    pr_repository: PullRequestRepository = Depends(get_pull_request_repository),
) -> Any:
    """Retrieve a single pull request by its UUID ID."""
    pr = await pr_repository.get_by_id(id)
    if not pr:
        raise EntityNotFoundError("Pull request not found.")
    return pr


@router.get(
    "/{id}/analyses",
    response_model=list[AnalysisSchema],
    tags=["pull-requests"],
    responses={
        200: {
            "description": "All analyses for this PR retrieved successfully.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "pull_request_id": "987f6543-e21b-34d5-c678-826614174111",
                            "status": "completed",
                            "summary": (
                                "Analysis completed with risk level HIGH "
                                "(Score: 75/100).\n"
                                "Findings:\n"
                                "- PR has been open for more than 30 days (42 days)"
                            ),
                            "risk_score": 75,
                            "risk_level": "HIGH",
                            "findings": [
                                "PR has been open for more than 30 days (42 days)"
                            ],
                            "created_at": "2026-06-14T12:00:00Z",
                            "updated_at": "2026-06-14T12:00:00Z",
                        }
                    ]
                }
            },
        }
    },
)
async def list_pull_request_analyses(
    id: uuid.UUID,
    pr_repository: PullRequestRepository = Depends(get_pull_request_repository),
    analysis_repository: AnalysisRepository = Depends(get_analysis_repository),
) -> Any:
    """List all analyses run against a PR sorted by created_at DESC."""
    pr = await pr_repository.get_by_id(id)
    if not pr:
        raise EntityNotFoundError("Pull request not found.")
    return await analysis_repository.list_by_pull_request(id)

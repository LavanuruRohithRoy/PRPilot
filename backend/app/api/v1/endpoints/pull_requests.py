import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_pull_request_repository
from app.repositories.pull_request import PullRequestRepository
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
        raise HTTPException(status_code=404, detail="Pull request not found.")
    return pr

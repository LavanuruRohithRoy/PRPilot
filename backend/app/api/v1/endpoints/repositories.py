import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_pull_request_repository, get_repository_repository
from app.repositories.pull_request import PullRequestRepository
from app.repositories.repository import RepositoryRepository
from app.schemas.pull_request import PullRequest as PullRequestSchema
from app.schemas.repository import Repository as RepositorySchema

router = APIRouter()


@router.get("", response_model=list[RepositorySchema], tags=["repositories"])
async def list_repositories(
    repo_repository: RepositoryRepository = Depends(get_repository_repository),
) -> Any:
    """List all registered repositories sorted alphabetically by full_name."""
    return await repo_repository.list_all()


@router.get("/{id}", response_model=RepositorySchema, tags=["repositories"])
async def get_repository(
    id: uuid.UUID,
    repo_repository: RepositoryRepository = Depends(get_repository_repository),
) -> Any:
    """Retrieve a single repository by its UUID ID."""
    repo = await repo_repository.get_by_id(id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    return repo


@router.get(
    "/by-name/{owner}/{name}", response_model=RepositorySchema, tags=["repositories"]
)
async def get_repository_by_name(
    owner: str,
    name: str,
    repo_repository: RepositoryRepository = Depends(get_repository_repository),
) -> Any:
    """Retrieve a single repository by its owner and name (full name)."""
    full_name = f"{owner}/{name}"
    repo = await repo_repository.get_by_full_name(full_name)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    return repo


@router.get(
    "/{id}/pull-requests", response_model=list[PullRequestSchema], tags=["repositories"]
)
async def list_repository_pull_requests(
    id: uuid.UUID,
    repo_repository: RepositoryRepository = Depends(get_repository_repository),
    pr_repository: PullRequestRepository = Depends(get_pull_request_repository),
) -> Any:
    """List all pull requests belonging to a specific repository UUID."""
    repo = await repo_repository.get_by_id(id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    return await pr_repository.list_by_repository(id)

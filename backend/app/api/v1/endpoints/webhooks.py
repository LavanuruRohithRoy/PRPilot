from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_db_session,
    get_github_sync_service,
    get_pull_request_repository,
    get_repository_repository,
)
from app.core.config import settings
from app.core.exceptions import DomainValidationError, EntityNotFoundError
from app.integrations.github.exceptions import GitHubWebhookVerificationError
from app.integrations.github.schemas.webhooks import (
    GitHubPullRequestEventPayload,
    GitHubRepositoryEventPayload,
)
from app.integrations.github.services import GitHubSyncService
from app.integrations.github.webhooks import verify_webhook_signature
from app.models.enums import PullRequestStatus
from app.repositories.pull_request import PullRequestRepository
from app.repositories.repository import RepositoryRepository

router = APIRouter()


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
    sync_service: GitHubSyncService = Depends(get_github_sync_service),
) -> dict[str, str]:
    """Handle incoming GitHub webhook events with signature verification."""
    body = await request.body()

    try:
        verify_webhook_signature(
            body, x_hub_signature_256, settings.GITHUB_WEBHOOK_SECRET
        )
    except GitHubWebhookVerificationError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e

    if not x_github_event:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header.")

    if x_github_event == "ping":
        return {"status": "ok"}

    try:
        if x_github_event == "repository":
            repo_payload = GitHubRepositoryEventPayload.model_validate_json(body)
            await sync_service.sync_repository(
                repo_payload.repository.owner.login, repo_payload.repository.name
            )
            return {"status": "synchronized"}

        elif x_github_event == "pull_request":
            pr_payload = GitHubPullRequestEventPayload.model_validate_json(body)
            repo = await sync_service.sync_repository(
                pr_payload.repository.owner.login, pr_payload.repository.name
            )
            await sync_service.sync_pull_request(repo.id, pr_payload.number)
            return {"status": "synchronized"}

    except (DomainValidationError, EntityNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"status": "ignored"}


@router.post("/github/test")
async def post_github_test(
    repo_repository: RepositoryRepository = Depends(get_repository_repository),
    pull_request_repository: PullRequestRepository = Depends(
        get_pull_request_repository
    ),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Offline dev test endpoint to directly upsert mock repositories
    and pull requests.
    """
    full_name = "test-owner/test-repo"
    repo = await repo_repository.get_by_full_name(full_name)
    if repo:
        repo = await repo_repository.update(
            repo,
            owner="test-owner",
            name="test-repo",
            full_name=full_name,
            is_active=True,
        )
    else:
        repo = await repo_repository.create(
            owner="test-owner", name="test-repo", full_name=full_name, is_active=True
        )

    await session.commit()
    await session.refresh(repo)

    pr = await pull_request_repository.get_by_repository_and_number(repo.id, 1)
    opened_at = datetime.now(UTC)
    if pr:
        pr = await pull_request_repository.update(
            pr,
            title="Test Pull Request",
            author="test-author",
            status=PullRequestStatus.OPEN,
            opened_at=opened_at,
        )
    else:
        pr = await pull_request_repository.create(
            repository_id=repo.id,
            pr_number=1,
            title="Test Pull Request",
            author="test-author",
            status=PullRequestStatus.OPEN,
            opened_at=opened_at,
        )

    await session.commit()
    await session.refresh(pr)

    return {
        "status": "synchronized",
        "repository": {
            "id": str(repo.id),
            "full_name": repo.full_name,
        },
        "pull_request": {
            "id": str(pr.id),
            "number": pr.pr_number,
            "title": pr.title,
            "status": pr.status,
        },
    }

from typing import Any

from app.integrations.github.schemas.pull_request import GitHubPullRequest
from app.integrations.github.schemas.repository import GitHubRepository
from app.models.enums import PullRequestStatus


def map_repository(dto: GitHubRepository) -> dict[str, Any]:
    """Map a GitHubRepository DTO to database attributes."""
    return {
        "owner": dto.owner.login,
        "name": dto.name,
        "full_name": dto.full_name,
        "is_active": True,
    }


def map_pull_request(dto: GitHubPullRequest) -> dict[str, Any]:
    """Map a GitHubPullRequest DTO to database attributes."""
    if dto.merged_at is not None:
        status = PullRequestStatus.MERGED
        closed_at = dto.merged_at
    elif dto.state == "closed":
        status = PullRequestStatus.CLOSED
        closed_at = dto.updated_at
    else:
        status = PullRequestStatus.OPEN
        closed_at = None

    return {
        "pr_number": dto.number,
        "title": dto.title,
        "author": dto.user.login,
        "status": status,
        "opened_at": dto.created_at,
        "closed_at": closed_at,
    }

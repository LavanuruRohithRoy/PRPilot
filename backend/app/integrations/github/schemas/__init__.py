"""PRPilot GitHub DTO transport schemas."""

from app.integrations.github.schemas.pull_request import GitHubPullRequest
from app.integrations.github.schemas.repository import GitHubRepository
from app.integrations.github.schemas.user import GitHubUser
from app.integrations.github.schemas.webhooks import (
    GitHubPullRequestEventPayload,
    GitHubRepositoryEventPayload,
)

__all__ = [
    "GitHubPullRequest",
    "GitHubPullRequestEventPayload",
    "GitHubRepository",
    "GitHubRepositoryEventPayload",
    "GitHubUser",
]

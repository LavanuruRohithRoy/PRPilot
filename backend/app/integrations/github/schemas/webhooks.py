from pydantic import BaseModel

from app.integrations.github.schemas.pull_request import GitHubPullRequest
from app.integrations.github.schemas.repository import GitHubRepository


class GitHubRepositoryEventPayload(BaseModel):
    """Validation DTO schema for GitHub repository event payloads."""

    action: str
    repository: GitHubRepository


class GitHubPullRequestEventPayload(BaseModel):
    """Validation DTO schema for GitHub pull request event payloads."""

    action: str
    number: int
    pull_request: GitHubPullRequest
    repository: GitHubRepository

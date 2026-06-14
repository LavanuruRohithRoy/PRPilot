from datetime import datetime

from pydantic import BaseModel

from app.integrations.github.schemas.user import GitHubUser


class GitHubPullRequest(BaseModel):
    """VCS DTO transport schema for a GitHub pull request."""

    id: int
    number: int
    title: str
    state: str
    html_url: str
    created_at: datetime
    updated_at: datetime
    merged_at: datetime | None = None
    user: GitHubUser

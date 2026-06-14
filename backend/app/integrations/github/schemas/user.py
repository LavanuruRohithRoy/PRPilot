from pydantic import BaseModel


class GitHubUser(BaseModel):
    """VCS DTO transport schema for a GitHub user profile."""

    id: int
    login: str
    avatar_url: str
    html_url: str

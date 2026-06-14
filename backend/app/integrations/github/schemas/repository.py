from pydantic import BaseModel

from app.integrations.github.schemas.user import GitHubUser


class GitHubRepository(BaseModel):
    """VCS DTO transport schema for a GitHub repository metadata."""

    id: int
    name: str
    full_name: str
    private: bool
    default_branch: str
    html_url: str
    owner: GitHubUser

class GitHubError(Exception):
    """Base exception class for all GitHub integration-level errors."""

    pass


class GitHubAuthenticationError(GitHubError):
    """Raised when GitHub token authentication fails (e.g. 401 Unauthorized)."""

    pass


class GitHubRateLimitError(GitHubError):
    """Raised when GitHub API rate limits are hit (e.g. 403 Rate Limit Exceeded)."""

    pass


class GitHubRequestError(GitHubError):
    """Raised when external GitHub HTTP requests fail."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class GitHubWebhookVerificationError(GitHubError):
    """Raised when incoming webhook signature verification fails."""

    pass

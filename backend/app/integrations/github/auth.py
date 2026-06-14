def build_github_headers(token: str | None = None) -> dict[str, str]:
    """Build standardized request headers for GitHub API communication."""
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "PRPilot-Client",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

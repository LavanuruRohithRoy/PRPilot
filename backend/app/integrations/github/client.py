from typing import Any

import httpx

from app.core.config import settings
from app.integrations.github.auth import build_github_headers
from app.integrations.github.exceptions import (
    GitHubAuthenticationError,
    GitHubRateLimitError,
    GitHubRequestError,
)


class GitHubClient:
    """Async client communicating with the GitHub REST API using generic primitives."""

    def __init__(self, api_url: str | None = None, token: str | None = None) -> None:
        self.api_url = api_url or settings.GITHUB_API_URL
        self.token = token or settings.GITHUB_TOKEN
        self.headers = build_github_headers(self.token)

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """Centralized request helper for HTTP requests."""
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method,
                    url,
                    headers=self.headers,
                    timeout=10.0,
                    **kwargs,
                )

                if response.status_code == 401:
                    raise GitHubAuthenticationError("GitHub authentication failed.")
                elif response.status_code == 403:
                    rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
                    if rate_limit_remaining == "0":
                        raise GitHubRateLimitError("GitHub API rate limit exceeded.")
                    raise GitHubRequestError("Access Forbidden.", response.status_code)
                elif not (200 <= response.status_code < 300):
                    raise GitHubRequestError(
                        f"GitHub request failed: {response.text}",
                        response.status_code,
                    )

                return response.json()
        except httpx.TimeoutException as e:
            raise GitHubRequestError(f"Request timeout: {e}") from e
        except httpx.RequestError as e:
            raise GitHubRequestError(f"Network request error: {e}") from e

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        """Perform an async GET request."""
        return await self._request("GET", endpoint, params=params)

    async def post(self, endpoint: str, json: dict[str, Any] | None = None) -> Any:
        """Perform an async POST request."""
        return await self._request("POST", endpoint, json=json)

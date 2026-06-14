# GitHub Integration Foundation

This document details the architectural boundaries and primitives of the GitHub integration layer in PRPilot.

## Architectural Boundaries

The GitHub integration layer serves as the boundary between the PRPilot system and the external GitHub REST API.
It is strictly limited to data transport, API interaction, and signature validation.

* **No Persistence**: The integration layer must never import ORM models or initiate database writes. All operations are local/transient transport operations.
* **DTO Isolation**: Data payloads are mapped to Pydantic transport-only DTO schemas (`GitHubUser`, `GitHubRepository`, `GitHubPullRequest`) located in `app.integrations.github.schemas`. This shields the core system from variations in external provider APIs.

## Authentication Flow

GitHub client authorization headers are generated statically by the `build_github_headers` function in `auth.py`.
If a personal access token or installation token is present, it is injected as a bearer authorization header.

## Client Design (`GitHubClient`)

The `GitHubClient` is a reusable wrapper class over `httpx.AsyncClient`.
* It handles base request logic, timeouts, and headers.
* It parses common HTTP error states (401, 403, and non-2xx status codes) and raises specialized integration-level exceptions like `GitHubAuthenticationError` and `GitHubRateLimitError`.

## Webhook Validation

To ensure incoming webhook request integrity, signature validation is performed in `webhooks.py` using HMAC SHA-256 digests.
Webhook endpoints must verify requests using `verify_webhook_signature(payload, signature, secret)`.

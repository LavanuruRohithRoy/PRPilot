# ADR 0005: GitHub Integration Foundation

## Status
Approved

## Context
We need to introduce a generic GitHub API client and signature verification helpers. This must be designed robustly to prevent database coupling or tight integration into background processing layers too early.

## Decisions

### 1. Choice of `httpx.AsyncClient`
We utilize `httpx.AsyncClient` inside a reusable `GitHubClient` wrapper class. This allows us to cleanly map async GET/POST methods and centralize timeout and headers settings without introducing heavyweight third-party libraries.

### 2. Strict DTO Decoupling from Database ORM
GitHub resource schema representation classes (`GitHubUser`, `GitHubRepository`, `GitHubPullRequest`) are declared as pure Pydantic transport DTOs in a standalone integration directory. Under no circumstances should they inherit from or directly couple with SQLAlchemy database ORM structures.

### 3. Dedicated Local/Transient Webhook Signature Verification
Incoming GitHub webhooks signature verification is implemented using standard HMAC SHA-256 computations in a stateless helper function. The validation runs locally and makes no database or network queries.

## Consequences
- The integration layer remains completely stateless and database-agnostic.
- Changes in the database schema do not break GitHub client contracts.
- Verification checks prevent malicious webhooks from executing business logic.

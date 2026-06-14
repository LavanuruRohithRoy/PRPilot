# GitHub Webhook Processing & E2E MVP Flow

This document details the webhook integration architecture, payload processing structures, read APIs, and local testing capabilities in PRPilot.

## Webhook Lifecycle Flow

PRPilot handles incoming GitHub events synchronously inside a single HTTP request thread, committing all modifications into PostgreSQL before returning a status code:

```
GitHub HTTP Request (Event Header)
       ↓
Webhook signature checks (HMAC SHA-256 validation)
       ↓
Event Payload Parsing (Pydantic schemas)
       ↓
Service Sync call (Stateless database upserts)
       ↓
Database Commit & Status Response
```

## Local Offline Test Endpoint

To support offline demonstrations without live VCS hooks or ngrok tunnels, the platform includes a dev-only route:
`POST /api/v1/webhooks/github/test`

When called, this endpoint directly interacts with the ORM repositories inside the current database session:
* Upserts a mock repository record `test-owner/test-repo`.
* Upserts a mock pull request `#1: Test Pull Request` under the repository.
* Commits the transaction to verify database operations.

## Repository and Pull Request APIs

All persistent entities are exposed via versioned GET endpoints:
* **`GET /api/v1/repositories`**: Returns all repositories sorted alphabetically by `full_name ASC`.
* **`GET /api/v1/repositories/{id}`**: Returns a single Repository by its UUID.
* **`GET /api/v1/repositories/by-name/{owner}/{name}`**: Returns a single Repository by owner and name lookup.
* **`GET /api/v1/repositories/{id}/pull-requests`**: Returns pull requests belonging to the Repository UUID.
* **`GET /api/v1/pull-requests/{id}`**: Returns a single Pull Request by its UUID.

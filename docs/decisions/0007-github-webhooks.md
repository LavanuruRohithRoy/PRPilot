# ADR 0007: GitHub Webhook Processing & E2E MVP Flow

## Status
Approved

## Context
We need to demonstrate a functional end-to-end integration flow from webhooks ingestion to database retrieval via REST APIs. This needs to be extremely reliable during local/demo runs.

## Decisions

### 1. Synchronous Webhook Processing
For simplicity and to maintain low infrastructure requirements at MVP validation time, webhooks are processed synchronously inside the request-response thread loop. Asynchronous queues (BackgroundTasks, Celery, Redis) are deferred to later stages.

### 2. Dev-Only Webhook Testing Endpoint
To guarantee robust demonstrations without live VCS hooks, network latency, or tunnel configuration failures, we expose a dev-only route:
`POST /api/v1/webhooks/github/test`

This endpoint bypasses HTTPX network calls and directly upserts mock data to verify PostgreSQL inserts, schema validation, and retrieval APIs.

### 3. Read APIs Database Wiring
We replace all legacy empty-array endpoint responses with actual database persistence select queries sorted alphabetically (`full_name ASC`) to return correct repository details.

## Consequences
- End-to-end flow is fully demonstrable using Swagger UI and PostgreSQL without external messaging dependencies.
- Local tests run instantly and predictably without requiring ngrok or live GitHub credentials.

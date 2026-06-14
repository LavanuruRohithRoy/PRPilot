# ADR 0004: API Foundation & Request Lifecycle

## Status
Approved

## Context
We need to lay down the API foundation and request lifecycle boundaries. This includes dependency injection patterns, router layouts, exception mapping strategies, and lifespan setup.

## Decisions

### 1. Isolated Lifespan Module
Instead of writing setup/teardown actions inside the main driver `main.py`, we isolate the database connection pool disposal context manager in `app.core.lifespan`. This maintains high cohesive separation of app configuration and server process setup.

### 2. Strict Database Session DI Provider
We implement only the database session provider `get_db_session` as a route dependency, resolving sessions safely. Repository dependencies are not created yet because no business endpoints are mapped.

### 3. Explicit JSON Error Response Scheme
Rather than leaving error representations generic, we define a strict schema (`ErrorResponse`) in `app.schemas.errors` with a `code` field constrained to a strict set of string literals:
- `"ENTITY_NOT_FOUND"`
- `"DOMAIN_VALIDATION_ERROR"`

This ensures that clients have a strongly typed machine-readable code for parsing.

### 4. Non-Dynamic Meta Route
We introduce `GET /api/v1/meta` returning a hardcoded dictionary mapping:
```json
{
  "service": "prpilot",
  "version": "0.1.0"
}
```
This serves strictly as a routing infrastructure sanity check without introducing pyproject parsing, file system requests, or extra settings complexity.

## Consequences
- Routing registration is type-safe and testable.
- The lifecycle cleanly tears down connection resources on SIGTERM/app shutdown.
- Custom exceptions raised anywhere in the route handlers map cleanly to our standard error contract.

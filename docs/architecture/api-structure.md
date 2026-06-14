# API Structure

This document outlines the API foundation and request/response lifecycles in PRPilot.

## Folder Organization

```
backend/app/
├── api/
│   ├── deps.py              # Central dependency injections (get_db_session)
│   ├── handlers.py          # Central exception handler functions
│   └── v1/                  # API v1 routes
│       ├── api.py           # V1 APIRouter registration root
│       └── endpoints/       # Specific router modules (meta)
└── core/
    ├── lifespan.py          # Application startup/shutdown lifespan context
    └── exceptions.py        # Custom domain exceptions
```

## Request/Response Lifecycle

The lifecycle follows this pathway:
1. **Connection Establishment**: Clients make HTTP requests. The FastAPI app resolves the endpoint handler.
2. **Dependency Resolution**: For routes that access the persistence layer, the `get_db_session` dependency context yields a connection-scoped SQLAlchemy `AsyncSession`.
3. **Execution**: The endpoint handler performs the route logic.
4. **Exception Handling**: If custom exceptions like `EntityNotFoundError` or `DomainValidationError` are raised, the registered exception mapper catches them, formats them into a standard `ErrorResponse` payload, and returns the appropriate HTTP status code.
5. **Lifespan Teardown**: Upon application shutdown, the engine's connection pool is cleanly discarded via `engine.dispose()`.

## Standard Error Response Payload

All custom exceptions are formatted and returned to the client matching the following schema:
- **`detail`** (string): Human-readable error message.
- **`code`** (string literal): Precise machine-readable code. Allowed codes:
  - `ENTITY_NOT_FOUND`
  - `DOMAIN_VALIDATION_ERROR`
- **`meta`** (dictionary, optional): Diagnostic parameters mapping strings to strings.

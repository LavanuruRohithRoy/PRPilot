# ADR 0002: Persistence Strategy & Database Infrastructure

## Status
Approved

## Context
PRPilot requires a highly performant, scalable relational database persistence strategy. We need to define libraries and design patterns that:
1. Support high-concurrency event handling without blocking the FastAPI event loop.
2. Provide database schema migration capabilities.
3. Decouple database technologies from business logic.
4. Establish secure identifiers suitable for public API routing.

## Decision

We adopt the following persistence technologies and design patterns:

1. **SQLAlchemy 2.0**:
   * **Why**: SQLAlchemy is the leading Python ORM. Version 2.0 brings native type safety with `Mapped` and `mapped_column`, is fully async-ready, and improves query compilation speeds.

2. **`AsyncSession` & `asyncpg`**:
   * **Why**: To prevent standard database drivers from blocking FastAPI’s single-threaded event loop. `asyncpg` is the fastest available PostgreSQL client library for Python.

3. **Alembic**:
   * **Why**: Alembic is the standard migration tool for SQLAlchemy. It integrates natively with SQLAlchemy models, supports async engines, and enables auto-generation of clean migration files.

4. **UUIDs for Primary Keys**:
   * **Why**: Instead of auto-incrementing integers, we use UUID4 (application-side default generation via `uuid.uuid4`). UUIDs prevent ID enumeration attacks, simplify integrations (Users, PullRequests, Reviews), and allow secure URL routing. Application-side default generation ensures portability and does not depend on database extension setups.

5. **Base Repository Pattern**:
   * **Why**: Promotes clean architecture. Restricting repositories to `BaseModel` (`ModelType = TypeVar("ModelType", bound=BaseModel)`) guarantees type safety. Services rely on the repository abstraction rather than database sessions, allowing easier mocking during testing.

## Consequences

* **Async-First Execution**: The entire database access flow is non-blocking.
* **Portable Keys**: Application-side UUID default generation is highly portable and eliminates dependency on custom database extensions (`pgcrypto`) during setup.
* **Type Correctness**: Strict `BaseModel` bounds prevent accidental data access leaks or operations on incorrect model classes.

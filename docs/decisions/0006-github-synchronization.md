# ADR 0006: GitHub Synchronization Layer Design

## Status
Approved

## Context
We need to sync repositories and pull requests from GitHub into our database persistence layer. We need to decide on service patterns, repository methods, DTO mappers, and transaction scopes.

## Decisions

### 1. Concrete `GitHubSyncService`
Rather than creating separate orchestrators for Repository and PullRequest synchronizations, we utilize a single concrete service class, `GitHubSyncService`, which implements `RepoSyncService`. This prevents service explosion and aligns with our minimalist approach.

### 2. Standardized Async CRUD Repository Methods
We extend the Repository pattern to include explicit CRUD persistence helper methods (`get_by_id`, `create`, `update`, `list_all`, etc.) on `RepositoryRepository` and `PullRequestRepository` classes, executing async SQLAlchemy 2.0 query patterns.

### 3. Service-Owned Database Transactions
Database session transaction hooks (`commit()`, `rollback()`, `refresh()`) are restricted entirely to the concrete synchronization service. Repository methods must never trigger transaction commits. One sync run represents exactly one database transaction context.

### 4. Dictionary DTO Mappings
DTO mapping functions convert external GitHub Pydantic objects directly into standard python dictionaries instead of constructing database ORM model instances. This prevents mapper components from needing database sessions or ORM class tracking.

## Consequences
- Repositories are clean data access objects with no transactional side-effects.
- Synchronizations are fully transactional, rolling back all session modifications upon any network or database failures.
- VCS integration layers are highly isolated and testable using mock objects.

# GitHub Synchronization Layer

This document details the architecture, mapping patterns, and transaction handling principles for the GitHub sync components in PRPilot.

## Synchronization Workflow

The sync layer integrates external VCS repository data into the local persistence layer synchronously.

```
External VCS (GitHub)
       ↓ (GitHubClient fetches DTO)
Mappers Layer (Translates DTO dict attrs)
       ↓
Sync Service (Orchestrates queries, upserts ORM via Repositories)
       ↓
AsyncSession (Commits transaction)
```

1. **GitHub API Request**: `GitHubSyncService` triggers client REST queries matching generic request formats.
2. **DTO to DB Attribute Mapping**: Extracted DTO structures are transformed into basic python dictionaries through specific mapping rules.
3. **ORM Database Upsert**:
   - Queries look up database records matching natural keys (`full_name` for repositories, `(repository_id, pr_number)` for pull requests).
   - If found, attributes are updated on the tracking ORM entity instance.
   - If missing, a new ORM entity is initialized and added to the session.

## Mapper Layer Separation

Mappers (`mappers.py`) do not reference repository instances, execute database connections, or trigger transaction commits. Their responsibilities are bounded entirely to mapping Pydantic objects to database field dictionaries. This limits coupling between VCS models and local database details.

## Database Transaction Boundaries

Database transaction commitment (`commit()`, `rollback()`, and `refresh()`) is strictly owned by the service layer:
* Repository operations must never call `commit()`.
* One sync request corresponds to a single logical database transaction. If any DB write or network parse fails during a sync workflow, the service rolls back the entire session.

## Error Handlers and Mappings

Network and authorization anomalies are caught at the sync service boundary and converted into clean application-level exceptions:
* `GitHubAuthenticationError` $\rightarrow$ `DomainValidationError`
* `GitHubRateLimitError` $\rightarrow$ `PRPilotError`
* `GitHubRequestError` $\rightarrow$ `PRPilotError`

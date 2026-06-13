# ADR 0003: Core Domain Boundaries & Persistence Strategy

## Status
Approved

## Context
As we introduce the first business domain layer for PRPilot (Repository, Pull Request, Analysis), we must establish clear architectural boundaries and persistence models that support future growth without locking us into early assumptions. This stage sets up the core domain model structures.

## Decisions

### 1. Separation of VCS Entities and Local Analysis Workflows
We explicitly decouple the sync state of VCS entities (Repositories, Pull Requests) from the local Analysis workflow execution metadata. The domain boundary separates:
- **Sync Context**: Captures standard read-only snapshots of external VCS entity attributes (`owner`, `name`, `full_name`, `pr_number`, `opened_at`, `closed_at`).
- **Analysis Context**: Tracks active state machines (`status`, `summary`, `risk_score`) related to our core product value (AI-driven pull request assessment).

### 2. Postponing User Identity Entities
Although pull requests are authored by users, we postpone the creation of a first-class `User` ORM entity at this stage.
- **Rationale**: An application-specific `User` model is tightly bound to OAuth flow patterns, token management, and role-based access control. Creating it now would introduce dead/untested code and premature constraints.
- **Approach**: The author of a Pull Request is stored as a simple string (`author`) containing the VCS user handle. Fully-typed authentication-level `User` structures will be introduced during the authentication stage.

### 3. VCS-Agnostic Service Interfaces
Service interfaces (`RepoSyncService` and `PRAnalysisService`) are defined abstractly to be VCS-provider agnostic.
- **Rationale**: While the initial implementation will support GitHub, the interface should support migrating or scaling to other providers (GitLab, Bitbucket, or standard git repos) without altering core analysis logic.

### 4. PostgreSQL Native Enum vs Check Constraints
For entity statuses (`PullRequestStatus` and `AnalysisStatus`), we choose native PostgreSQL `ENUM` types mapped via SQLAlchemy 2.0 `Enum` type objects.
- **Rationale**: Native database enums provide a clean, type-safe representation in PostgreSQL and prevent invalid statuses from entering the tables.

### 5. Application-Level Concurrency Constraints
The business rule enforcing that a pull request can have only one active analysis (`pending` or `running`) at a time is implemented at the application/service layer rather than as a complex database constraint (e.g. conditional index).
- **Rationale**: Decoupling this constraint from the database schema allows for greater flexibility (e.g. easily changing the limit or behavior in future updates, queuing requests, or supporting historical re-runs) without performing database schema migrations.

## Consequences
- The database schema stays simple, clean, and highly portable.
- Adding support for other code hosts requires creating concrete service implementations of our abstract service definitions without altering the ORM definitions.
- Alembic database migrations cleanly autogenerate all tables, indexes, relationships, and native enums with an automated, fully reversible downgrade path.

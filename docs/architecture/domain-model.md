# Core Domain Models

This document describes the core business entities, their constraints, validation rules, relationships, and invariants in PRPilot.

## Entities and Schemas

### 1. Repository
Represents a source code repository synced from a VCS provider (e.g. GitHub).
- **Entity Identification**: Primary key is a system-generated UUID (UUID4).
- **Properties**:
  - `owner` (string, index): The owner of the repository (user or organization).
  - `name` (string, index): The name of the repository.
  - `full_name` (string, unique, index): Unique identifier representing `<owner>/<name>`.
  - `is_active` (boolean, default `True`): Toggles platform tracking for this repository.
- **Relationships**:
  - `pull_requests`: One-to-many relationship with `PullRequest` entity. Deleting a repository cascades to delete all associated pull requests.

### 2. Pull Request
Represents a pull request snapshot synchronized from the VCS provider.
- **Entity Identification**: Primary key is a system-generated UUID (UUID4).
- **Properties**:
  - `repository_id` (UUID, Foreign Key, index): ID of the parent `Repository`.
  - `pr_number` (integer, index): The pull request number from the code host.
  - `title` (string): The title of the pull request.
  - `author` (string): The user account that opened the pull request.
  - `status` (PullRequestStatus): Current status, represented as a native DB enum mapping to values: `open`, `closed`, `merged`.
  - `opened_at` (timezone-aware datetime): Time when the PR was originally opened.
  - `closed_at` (timezone-aware datetime, optional): Time when the PR was closed or merged.
- **Relationships**:
  - `repository`: Many-to-one relationship with `Repository`.
  - `analyses`: One-to-many relationship with `Analysis` entity. Deleting a pull request cascades to delete all associated analyses.

### 3. Analysis
Represents an AI-powered intelligence run on a pull request.
- **Entity Identification**: Primary key is a system-generated UUID (UUID4).
- **Properties**:
  - `pull_request_id` (UUID, Foreign Key, index): ID of the parent `PullRequest`.
  - `status` (AnalysisStatus): Current run status, represented as a native DB enum mapping to values: `pending`, `running`, `completed`, `failed`.
  - `summary` (text, optional): Generated text summary of the pull request risk analysis.
  - `risk_score` (integer, optional): The calculated risk score rating.
- **Relationships**:
  - `pull_request`: Many-to-one relationship with `PullRequest`.

---

## Core Domain Invariants and Constraints

### Uniqueness Constraints
1. **Repository Full Name**: The `full_name` column on the `repositories` table is marked as `unique=True` (and backed by an index) to ensure that the system does not register the same repository twice.
2. **Repository + Pull Request Number**: The combination of `(repository_id, pr_number)` is globally unique. This is enforced at the database level by the unique constraint `uq_repository_pr_number` on the `pull_requests` table.

### Range Boundaries
- **Risk Score**: The `risk_score` on the `analyses` table must be an integer between `0` and `100` inclusive. This is enforced by:
  - Database: A PostgreSQL `CheckConstraint` named `chk_analysis_risk_score` with condition `risk_score >= 0 AND risk_score <= 100`.
  - Application Schema: A Pydantic schema validation using `Field(ge=0, le=100)`.

### Status Machine Transitions
- **Pull Request Status**:
  - Allowed states: `open`, `closed`, `merged`.
- **Analysis Status**:
  - Allowed states: `pending`, `running`, `completed`, `failed`.
  - Typical lifecycle transition: `pending` -> `running` -> `completed` or `failed`.

### Concurrency and Soft Constraints
- **Single Active Analysis per PR**: At any time, there can be at most one active analysis (`pending` or `running`) for a single pull request. This constraint is decoupled from the database schema to maintain agility, and will be enforced programmatically by the application service layer when analyses are triggered.

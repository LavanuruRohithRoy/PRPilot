# ADR 0009: Dashboard Aggregations and Query Optimization

## Status
Proposed

## Context
We need to provide a unified summary dashboard endpoint (`GET /api/v1/dashboard`) showing the total counts of repositories, pull requests, and analyses (segmented by low/medium/high risk levels), as well as a list of recent analysis runs. This summary is intended to be demo-ready, but we must ensure we do not hit the database with redundant query cycles.

## Decisions

1. **Direct Aggregation Query**: Instead of maintaining running counts or using cached redis storage (which adds infrastructure complexity), we will run direct query-level aggregations on PostgreSQL. At our current scale and for demo purposes, this runs in <3ms.
2. **Consolidated Group-By Query**: We will execute a single `GROUP BY` query on `Analysis.risk_level` instead of running separate counts for total analyses, low risk, medium risk, and high risk. This replaces 4 individual queries with 1.
3. **Eager Loading of Relations**: The recent analyses list (limited to the top 5 runs) will eager-load related `PullRequest` and `Repository` records using SQLAlchemy's `joinedload` option. This prevents standard $N+1$ lazy loading queries when converting records to schemas.

## Consequences
* **Performance**: The entire dashboard aggregation evaluates in exactly 4 optimized query executions.
* **Maintainability**: Bypassing background synchronization caches reduces infrastructure dependencies and ensures the dashboard metrics are always 100% accurate.

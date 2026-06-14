# ADR 0008: Deterministic PR Analysis Engine and Table Expansion

## Status
Proposed

## Context
We need to introduce the first pull request analysis features to PRPilot. Pull request analysis requires evaluating pull request snapshots for potential risk indicators (e.g., WIP status, stale branches, overly brief title descriptions). We must support score calculation, risk classification, structured findings tracking, and persistence.

## Decisions

1. **Synchronous Execution**: The analysis engine will execute synchronously within the request lifecycle. We bypass background workers (Celery, Redis) to simplify deployment and testing for the initial MVP.
2. **Deterministic Rule Engine**: To guarantee 100% test reliability and zero external api latencies/costs, we implement a rule-based engine instead of calling LLMs.
3. **Type-Safe `RiskLevel` Enum**: We define a Python `StrEnum` and persist it as a native enum type (`risklevel`) in PostgreSQL. This makes the database and the API schema type-safe, preventing deserialization conflicts and improving Swagger typing.
4. **JSON-Structured `findings` Column**: We store the list of detected issues (`findings`) in a PostgreSQL `JSON` database column. This prevents raw string formatting contamination and allows API consumers to parse structured findings directly.
5. **No Risk Increases for Merged PRs**: Merged pull requests do not accumulate risk scores. They are generally considered low risk once merged.

## Consequences
* **Performance**: Synchronous database lookup and simple rule execution run in <5ms, ensuring rapid API responses.
* **Storage Size**: JSON columns add small, negligible overhead to postgres.
* **Extensibility**: The clean separation between the database schema, Pydantic responses, and the rule engine allows us to transition to an LLM provider seamlessly in the future by updating the service implementation class.

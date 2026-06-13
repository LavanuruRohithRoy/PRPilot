# ADR 0001: Local Tooling & Code Quality Standards

## Status
Approved

## Context
PRPilot is an AI-powered Pull Request Intelligence Platform with a Next.js frontend, a FastAPI backend, and integrations with Postgres, Redis, and AI services. To support rapid iteration and maintain high code quality across contributors, we need unified styling, static code checks, strict typing boundaries, and efficient dependency package management.

We must decide on our toolchains for formatting, linting, type safety, git pre-hooks, and package management in both Python (backend) and Node.js (frontend).

## Decision

We adopt the following tools and standards for development tooling:

1. **`uv` over standard `pip`/`poetry`**:
   * **Why**: `uv` is a blazing-fast Python package manager written in Rust. It offers order-of-magnitude faster installations and compiles dependencies without the overhead of heavy virtual environment managers. We declare development optional-dependencies using standard `project.optional-dependencies` for maximum ecosystem compatibility.

2. **`Ruff` over `Black` / `Flake8` / `isort`**:
   * **Why**: `Ruff` replaces multiple disconnected linting and formatting engines (Black, Flake8, isort, autoflake) with a single, highly performant Rust-based tool. This significantly speeds up local code verification checks and simplifies pre-commit configuration.

3. **`MyPy` for static type checks**:
   * **Why**: Python's type annotations catch syntax and logic bugs before execution. We enforce MyPy annotations across all backend function inputs and return variables (`disallow_untyped_defs = true`, `check_untyped_defs = true`, `warn_unused_ignores = true`) to prevent type decay and reduce runtime bugs.

4. **`pre-commit` for local code gatekeeping**:
   * **Why**: To prevent low-quality code (syntax errors, formatting anomalies, unorganized imports) from reaching remote repository branches. Runs checks for `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `ruff`, and `ruff-format` locally at checkout before commits are finalized.

5. **`pnpm` over `npm` / `yarn`**:
   * **Why**: `pnpm` offers fast, space-efficient workspace structures. It uses a content-addressable store to save disk space and avoids nesting duplicative node modules across subdirectories, supporting clean monorepo layouts.

## Consequences

* **Unified Style**: Automated code styling guarantees consistency and reduces styling discussions in code reviews.
* **Rapid CI/CD**: Local validation shifts code quality checks left, preventing invalid PR builds on the remote pipeline.
* **Typing Overhead**: Writing full type hints increases initial code formulation time but increases maintenance and reading speed for agents, teammates, and Copilot tools.

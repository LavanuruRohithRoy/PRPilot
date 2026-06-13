# Development Standards & Code Quality Guidelines

This document outlines the development conventions, style guides, static check routines, commit specifications, and the Definition of Done (DoD) for the PRPilot project.

---

## 1. Architecture Rules

* **Single Responsibility**: Each module, class, function, or component must fulfill exactly one well-defined responsibility.
* **No Dead Code**: Prohibit keeping unused functions, variables, modules, or configurations in the active codebase. Unreachable blocks must be deleted immediately.
* **No Commented-out Code**: Implementations that are commented out must not be committed to Git. If code is no longer needed, remove it; history can be retrieved via Git.
* **No Utility Dumping Grounds**: The creation of generic helper files like `utils.py`, `helpers.py`, or `misc.py` is banned. Utility functions must reside in cohesive, context-specific domains (e.g., `backend/app/core/security.py`).

---

## 2. Dependency Direction

* **Strict Inward Flow**: Source code dependencies must always point inward from outer presentation/API boundaries toward inner service orchestration layers.
* **Layer Boundaries**:
  * **API Controllers** depend on **Services**.
  * **Services** depend on **Repositories** and **Agents**.
  * **Repositories** depend on **Models**.
* **Forbidden References**:
  * Repositories must never be imported directly inside API routes. All queries must flow through the service layer.
  * Services must never depend on Agents to prevent circular cycles.

---

## 3. Backend Standards

Python backend code uses `uv` for package management, `Ruff` for linting/formatting, and `MyPy` for type checks.

### Linting & Formatting Rules
* **Formatting Engine**: `Ruff` is the exclusive formatter. Do not run Black, Flake8, or isort.
* **Rules Enforced**: Lint rules are configured in `pyproject.toml` (specifically rules `E`, `W`, `F`, `I`, `B`, `C4`, `UP`, `RUF`).
* **Strings**: Double quotes (`"`) are enforced.
* **Indentation**: 4 spaces are enforced.

### Type Safety Rules
* **Type Annotations**: All backend function parameters, variables, and return types must be fully annotated.
* **MyPy Strictness**: MyPy runs type evaluation checks. While `strict` is set to false for flexibility, `check_untyped_defs = true`, `disallow_untyped_defs = true`, and `warn_unused_ignores = true` are strictly enforced to prohibit untyped code paths and redundant type ignores.

---

## 4. Frontend Standards

Frontend development uses `pnpm` for package management, `ESLint` for code check gates, and `Prettier` for styling.

* **Formatting Rules**:
  * Double quotes (`"`) are used.
  * Semicolons (`semi: true`) are required.
  * Trailing commas must follow `es5` compatibility rules.
* **Type Safety**: TypeScript-oriented strictness will be fully activated upon initialization. All custom components, parameters, state arrays, and API responses must have strict interfaces.
* **Clean Code**: No unused variables (except variables prefixed with an underscore `_`), unused imports, or `console.log` statements (except `console.warn` or `console.error` for errors) are allowed in commits.

---

## 5. Git Commit Standards

* **Conventional Commits**: Commit messages must follow the [Conventional Commits spec](https://www.conventionalcommits.org/):
  * `feat: ...` for new features or infrastructure additions.
  * `fix: ...` for bugs.
  * `chore: ...` for configuration adjustments, dependencies, or standard rules documentation updates.
  * `docs: ...` for project documentation files.
* **Granularity**: Keep commits small and atomic. Each commit should focus on one logical change.

---

## 6. Copilot Usage Rules

* **Semantic Understanding**: Do not blindly copy AI-generated templates. Ensure every line of generated code is fully understood and integrates correctly into the architecture.
* **No Placeholders**: Never commit files containing comments like `# TODO: implement this` or `// placeholder`. The code must represent a clean, completed step.
* **No Mock Logic**: No fake repositories, mock response objects, or simulated routes can be committed unless explicitly authorized under testing directories.

---

## 7. Definition of Done (DoD)

Before any task or stage is marked complete and submitted for review, the following checks must be verified:

1. **Tooling Validation**:
   * Running `uv run ruff check .` reports no warnings or lint errors.
   * Running `uv run ruff format --check .` reports correct formatting.
   * Running `uv run mypy .` reports successful compilation and type checking.
2. **Local Pre-commit Gate**:
   * Pre-commit hooks (`trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `ruff`, `ruff-format`) must execute and pass without error.
3. **No Drift**:
   * Ensure changes conform to the layers specified in the project structure architecture documentation.
4. **No Code Clutter**:
   * Code is devoid of unused imports, dead/unreachable blocks, debug log statements, or placeholder code comments.
5. **No Untyped Code**:
   * No functions are left untyped.
6. **Documentation Updated**:
   * Any configuration changes or architectural modifications are recorded.

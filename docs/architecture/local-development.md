# Local Development Container Architecture

This document describes the container architecture, service design, networking, and configuration conventions of the local development environment for PRPilot.

---

## 1. Container Architecture

PRPilot is designed to run locally using a set of Docker containers to ensure environment reproducibility across development machines.

```mermaid
graph TD
    User[Developer] -->|localhost:3000| Frontend[prpilot-frontend]
    User -->|localhost:8000| Backend[prpilot-backend]
    
    subgraph Shared Bridge Network: prpilot-network
        Frontend
        Backend
        Backend -->|postgres:5432| Postgres[(prpilot-postgres)]
        Backend -->|redis:6379| Redis[(prpilot-redis)]
    end
```

---

## 2. Service Responsibilities

### `backend` (FastAPI)
* **Image**: Built dynamically using `backend/Dockerfile` based on `python:3.11-slim`.
* **Tooling**: Adopts `uv` as the package installer to compile environment packages (`fastapi`, `uvicorn`).
* **Volume Mount**: Bind-mounts the `backend/` directory to `/app` inside the container to enable live code reloading.
* **Role**: Runs the main FastAPI REST application.

### `frontend` (Next.js Placeholder)
* **Image**: Built dynamically using `frontend/Dockerfile` based on `node:20-slim`.
* **Tooling**: Enables `corepack` and activates `pnpm` for future dependency loading.
* **Volume Mount**: Bind-mounts the `frontend/` directory to `/app`.
* **Role**: Stays alive using a passive command (`tail -f /dev/null`) until the Next.js React codebase is initialized.

### `postgres` (PostgreSQL Database)
* **Image**: Uses the official `postgres:15-alpine` image to save space and minimize system footprint.
* **Role**: Primary data store for relational tables.
* **Persistence**: Named volume `prpilot_postgres_data` mapping to `/var/lib/postgresql/data` ensures data persists across container lifecycles.

### `redis` (Redis Cache / Message Broker)
* **Image**: Uses the official `redis:7-alpine` image.
* **Role**: In-memory data store for caching, token storage, and background task signaling.

---

## 3. Networking Overview

All containers join a custom docker bridge network named `prpilot-network`. 

* **DNS Resolution**: Containers communicate internally using their service names as hosts (e.g. `postgres:5432`, `redis:6379`).
* **Isolation**: Limits traffic exposure to local system developer environments and mitigates port collisions.

---

## 4. Environment Configuration

Configuration variables are parsed from the `.env` file at the root of the workspace (specified using the `env_file` property pointing to `../../../.env` for the backend, frontend, and postgres services). A template is maintained at `.env.example`.

| Variable | Description | Development Default |
| :--- | :--- | :--- |
| `POSTGRES_DB` | Relational database namespace | `prpilot` |
| `POSTGRES_USER` | Relational database superuser | `postgres` |
| `POSTGRES_PASSWORD` | Relational database password | `postgres` |
| `DATABASE_URL` | SQLAlchemy connection string | `postgresql://postgres:postgres@postgres:5432/prpilot` |
| `REDIS_URL` | Redis server connection string | `redis://redis:6379` |
| `BACKEND_PORT` | Port exposed to host machine for Backend | `8000` |
| `FRONTEND_PORT` | Port exposed to host machine for Frontend | `3000` |

---

## 5. Startup & Dependency Sequencing

The container configuration ensures that service health governs dependency loading sequence:

1. **`postgres` & `redis`** are launched first.
2. **`postgres` healthcheck** runs `pg_isready -U $POSTGRES_USER -d $POSTGRES_DB` until database connection is verified.
3. **`redis` healthcheck** runs `redis-cli ping` until connection is successful.
4. **`backend`** starts only after both database and cache instances report `service_healthy`.
5. **`backend` healthcheck** verifies server availability by executing a python script to request the `GET /health` API endpoint.

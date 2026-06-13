# Local Development Docker Workspace

This directory contains the Docker Compose environment configs for local development.

---

## Prerequisites

1. Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine is installed and running.
2. Initialize your `.env` configuration file from the template in the root directory:
   ```bash
   cp .env.example .env
   ```

---

## CLI Reference Guide

All commands must be executed from the configuration context directory:
```bash
cd infrastructure/docker/compose
```

### Start Services
Spin up the backend, frontend, postgres database, and redis cache in the background:
```bash
docker compose up -d --build
```
*The `--build` flag ensures Docker compiles the Dockerfiles with any newly installed packages.*

### View Output logs
Stream output logs of all services or target a specific one (e.g. backend):
```bash
# All logs
docker compose logs -f

# Backend only
docker compose logs -f backend
```

### Stop Services
Stop and tear down the running containers while leaving Postgres databases persisted:
```bash
docker compose down
```

### Full Clean Down
Tear down the environment and wipe out Postgres database volumes to start with a clean slate:
```bash
docker compose down -v
```

---

## Local Development Workflow

* **Hot Reloading**: The backend and frontend directories are mounted as bind volumes to `/app` inside their respective containers. Any local modifications will trigger live server updates.
* **Adding dependencies (Python)**: When you add packages to `backend/pyproject.toml`, run `docker compose build backend` to rebuild the backend image.

# PRPilot — AI-Powered Pull Request Intelligence Platform

PRPilot is an intelligent, developer-focused Pull Request Intelligence Platform that automates code reviews, performs rule-based risk assessments, and provides interactive grounded repository Q&A retrieval.

By leveraging **Microsoft Azure AI Foundry** and standard Azure OpenAI GPT models, PRPilot provides deep visibility into codebase health, identifying vulnerabilities and WIP markers directly within the developer's deployment workflow.

---

## 1. Problem Statement

Modern software development moves at high velocities, resulting in:
*   **Cognitive Reviewer Fatigue**: Reviewers are overwhelmed by repetitive syntax, styling, and basic pattern validations.
*   **Undetected Risk Vectors**: Out-of-order merging, missing tests, and Work-In-Progress (WIP) leakage introduce bugs into main branches.
*   **Information Disconnection**: New developers struggle to query across pull requests and existing risk analysis records to answer architectural questions.

PRPilot bridges this gap by offering a rule-based deterministic risk-analysis engine combined with an interactive **Microsoft Foundry IQ** grounded search interface.

---

## 2. Architecture Overview

PRPilot is built with a decoupled monorepo architecture separating the FastAPI backend, React/Vite frontend, and Azure AI Foundry integrations:

```mermaid
flowchart TD
    subgraph Client Application
        Web[React Dashboard UI]
        Dev[CLI / API Client]
    end

    subgraph FastAPI Backend App
        API[API Router]
        Sync[GitHub Sync Service]
        Engine[Risk Analysis Engine]
        FoundryService[FoundryIQService]
    end

    subgraph Data & Storage
        DB[(PostgreSQL)]
        Snapshot[Local JSON Snapshot]
    end

    subgraph Microsoft Azure Cloud
        Model[GPT-4o Deployment]
    end

    %% Webhook ingestion
    VCS[GitHub Webhooks] -->|POST /api/v1/webhooks/github| API
    API -->|1. Sync Metadata| Sync
    Sync -->|2. Persist Records| DB

    %% Analysis
    Sync -->|3. Trigger Assessment| Engine
    Engine -->|4. Store Scores & Findings| DB

    %% Grounded Q&A
    API -->|GET /api/v1/dashboard| DB
    API -->|POST /api/v1/intelligence/ingest| FoundryService
    FoundryService -->|Read DB Records| DB
    FoundryService -->|Write Snapshot| Snapshot

    Dev -->|GET /api/v1/intelligence/query| API
    API -->|Invoke completions| FoundryService
    FoundryService -->|Read Snapshot| Snapshot
    FoundryService -->|5. Submit Grounded Prompt| Model
    Model -->|6. Return Citations & Answer| FoundryService
    FoundryService -->|GroundedQueryResponse| Dev
```

---

## 3. Tech Stack

*   **Core Backend**: Python 3.11, FastAPI, SQLAlchemy (PostgreSQL driver), Pydantic v2
*   **Frontend**: React 18, Vite 4, TypeScript, Recharts
*   **Verification & Quality**: Pytest, Ruff, Mypy
*   **AI Integration**: Azure AI Projects (`azure-ai-projects`), Azure Identity (`azure-identity`), OpenAI API
*   **Data Tier**: PostgreSQL, Local temporary JSON Storage

---

## 4. Key Features

1.  **GitHub Event Synchronizer**: Verifies secure webhook signature headers, ingests PR event payloads, and tracks repositories, author, and branch status.
2.  **Risk Analysis Engine**: Applies deterministic scoring (flagging title length, open duration, WIP markers, and file changes) and categorizes risks (`LOW`, `MEDIUM`, `HIGH`).
3.  **Dashboard API**: Exposes aggregated system metrics (PR counts, repository list, counts by risk level, and recent analysis runs) via a single database query call.
4.  **Foundry IQ Grounded Q&A**: Answers questions regarding pull requests, risk assessments, and repository trends using strict local grounding snapshots to avoid hallucinations.

---

## 5. Hackathon Submission: Microsoft Foundry IQ Usage

To enable seamless deployments in regions where Azure AI Foundry Agents are not supported (e.g. **Central India**), PRPilot runs in a lightweight, robust **Agentless Compatibility Mode**:

*   **Local Grounding Snapshot**: During ingestion (`POST /intelligence/ingest`), PRPilot dumps synchronized database records into a local JSON snapshot.
*   **Structured Prompting**: The Q&A endpoint formats the snapshot contents into a markdown context with pre-allocated citation keys (e.g. `[pr_1_5]`).
*   **Authentication & Inference**: The service fetches the Azure OpenAI client dynamically using either Entra ID (`DefaultAzureCredential`) or a direct project API key, submitting grounded prompts in JSON Mode.
*   **hallucination Prevention**: Output references are mapped strictly back to authenticated PostgreSQL repository and PR analysis IDs, ensuring 100% accurate, non-hallucinated citations.

---

## 6. Project Structure

```text
prpilot/
├── backend/                  # Python FastAPI Backend
│   ├── app/
│   │   ├── api/              # API endpoints and dependency injection
│   │   ├── core/             # Configuration settings and exceptions
│   │   ├── models/           # SQLAlchemy database model models
│   │   ├── schemas/          # Pydantic serialization schemas
│   │   └── services/         # Business logic (Analysis, Sync, FoundryIQ)
│   ├── tests/                # Unit and Integration test suites
│   ├── verify_foundry.py     # Runtime connectivity verification script
│   └── .env.example          # Sample environment settings file
├── docs/                     # Platform Specifications
│   ├── architecture/         # Architectural flow diagrams
│   └── decisions/            # Architectural Decision Records (ADRs)
└── frontend/
    └── prpilot-ui/           # React + Vite Dashboard (TypeScript)
```

---

## 7. Environment Variables Configuration

Copy `backend/.env.example` to `backend/.env` and configure:

| Key | Description | Example Value |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://postgres:postgres@localhost:5432/prpilot` |
| `GITHUB_TOKEN` | Personal Access Token (PAT) | `github_pat_xxxx` |
| `GITHUB_WEBHOOK_SECRET` | Secret to sign webhook headers | `your-secret-here` |
| `AZURE_OPENAI_ENDPOINT` | Direct Azure OpenAI Endpoint | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API Key | `your-azure-key-here` |
| `AZURE_OPENAI_DEPLOYMENT_NAME`| Model deployment name | `gpt-4o` |
| `AZURE_AI_FOUNDRY_CONNECTION_STRING` | Optional connection string | `region.api.azureml.ms;sub;rg;project` |

---

## 8. Local Setup Instructions

### Prerequisites
*   Python 3.11+
*   PostgreSQL Database
*   `uv` package manager (`pip install uv`)
*   Node.js 18+ and npm

### Steps
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/LavanuruRohithRoy/PRPilot.git
    cd PRPilot/backend
    ```
2.  **Configure environment**:
    Create `.env` file from the template and set the connection parameters.
3.  **Install Dependencies & Setup virtual environment**:
    ```bash
    uv venv
    uv pip install -e .[dev]
    ```
4.  **Run Migrations**:
    ```bash
    uv run alembic upgrade head
    ```
5.  **Run Verification Script**:
    ```bash
    uv run python verify_foundry.py
    ```
6.  **Run Backend Server**:
    ```bash
    uv run uvicorn app.main:app --reload
    ```
7.  **Run Frontend** (separate terminal):
    ```bash
    cd ../frontend/prpilot-ui
    npm install
    npm run dev
    # → http://localhost:5173
    ```

---

## 9. API Endpoints Summary

| Method | Route | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/webhooks/github` | Ingests secure webhook event actions from GitHub |
| `GET` | `/api/v1/dashboard` | Returns system-wide aggregated counts and recent analyses |
| `GET` | `/api/v1/repositories` | Lists all registered repositories |
| `GET` | `/api/v1/pull-requests` | Lists all pull requests across all repositories |
| `GET` | `/api/v1/analyses` | Lists all analysis records ordered by recency |
| `POST` | `/api/v1/intelligence/ingest` | Compiles SQL records into the local grounding snapshot |
| `GET` | `/api/v1/intelligence/query` | Executes grounded Q&A over repositories and pull requests |

---

## 10. Documentation Index

Detailed architectural specifications, workflows, and ADRs are mapped below:

### Architecture
*   [Foundry IQ Integration](file:///docs/architecture/foundry-iq.md): Detailed workflow on local grounding snapshot building, prompt compilation, and completions routing.
*   [Dashboard Metric Aggregation](file:///docs/architecture/dashboard.md): Summary of single-query counts aggregation.

### Decisions History (ADRs)
*   [ADR 0010: Agentless RAG Grounding](file:///docs/decisions/0010-foundry-iq-grounding.md): Rationales for removing managed agents, vector stores, and blob storages to accommodate Central India region support.
*   [ADR 0009: Dashboard Aggregations](file:///docs/decisions/0009-dashboard-summary.md): DB counts query design decisions.

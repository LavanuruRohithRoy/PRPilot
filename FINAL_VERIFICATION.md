# PRPilot - Final Submission Verification Guide

This document is a step-by-step guide designed to help judges verify the complete end-to-end functionality of PRPilot in under 5 minutes.

---

## Prerequisites
Ensure the environment variables are loaded in `backend/.env`. Refer to [README.md](file:///c:/Users/DELL/Rohith/PRPilot/README.md) for variable keys.

---

## Step 1: Database Setup & Migrations (30 seconds)
Run migrations to initialize the PostgreSQL database schema:
```powershell
cd backend
uv run alembic upgrade head
```
Expected output:
`INFO  [alembic.runtime.migration] Running upgrade  ->  ...`

---

## Step 2: Runtime Connectivity Check (30 seconds)
Verify Microsoft AI Foundry / Azure OpenAI deployment connectivity:
```powershell
uv run python verify_foundry.py
```
Expected output:
```text
[OK] Azure API key and endpoint detected (or Connection String)
[OK] Deployment reachable
[OK] Completion generated
[OK] Foundry integration verified
```

---

## Step 3: Startup Backend Server (15 seconds)
Start the FastAPI server:
```powershell
uv run uvicorn app.main:app --reload --port 8000
```
Server Swagger documentation will be available at: `http://localhost:8000/docs`

---

## Step 4: Simulate GitHub Webhook Synchronization (45 seconds)
Simulate a webhook event from GitHub representing a new pull request:
```powershell
curl -X POST "http://localhost:8000/api/v1/webhooks/github" `
  -H "Content-Type: application/json" `
  -H "X-GitHub-Event: pull_request" `
  -H "X-Hub-Signature-256: sha256=mock-signature" `
  -d '{
    "action": "opened",
    "repository": {
      "id": 123456,
      "name": "test-repo",
      "owner": { "login": "test-owner" },
      "full_name": "test-owner/test-repo",
      "private": false
    },
    "pull_request": {
      "id": 987654,
      "number": 42,
      "title": "WIP: Add database cache integration",
      "user": { "login": "dev-author" },
      "state": "open",
      "created_at": "2026-06-14T12:00:00Z",
      "updated_at": "2026-06-14T12:00:00Z"
    }
  }'
```
Expected response:
`{"status":"success","action":"opened","pull_request_number":42}`

*Note: The backend automatically triggers the **Risk Analysis Engine** synchronously on pull request creation.*

---

## Step 5: Verify Dashboard Aggregation (30 seconds)
Verify that the pull request, repository, and risk analysis metrics are registered:
```powershell
curl -X GET "http://localhost:8000/api/v1/dashboard"
```
Expected response format:
```json
{
  "repositories": 1,
  "pull_requests": 1,
  "analyses": 1,
  "high_risk": 1,
  "medium_risk": 0,
  "low_risk": 0,
  "recent_analyses": [
    {
      "id": "analysis-uuid",
      "repository_name": "test-owner/test-repo",
      "pr_number": 42,
      "pr_title": "WIP: Add database cache integration",
      "risk_score": 15,
      "risk_level": "HIGH",
      "created_at": "2026-06-14T..."
    }
  ]
}
```

---

## Step 6: Grounding Ingestion (30 seconds)
Serialize PostgreSQL records to the local grounding snapshot:
```powershell
curl -X POST "http://localhost:8000/api/v1/intelligence/ingest"
```
Expected response:
```json
{
  "repositories": 1,
  "pull_requests": 1,
  "analyses": 1,
  "status": "knowledge_refreshed"
}
```

---

## Step 7: Grounded Q&A Retrieval (45 seconds)
Execute a grounded RAG query referencing the pull request records and risk analysis findings:
```powershell
curl -G "http://localhost:8000/api/v1/intelligence/query" --data-urlencode "query=Which repository contains high risk pull requests?"
```
Expected response format:
```json
{
  "query": "Which repository contains high risk pull requests?",
  "answer": "The repository test-owner/test-repo contains a high-risk pull request #42 [pr_1_42], flagged for WIP markers.",
  "citations": [
    {
      "id": "pr_1_42",
      "title": "PR #42 (test-owner/test-repo) - Risk Level: HIGH",
      "url": "https://api.github.com/test-owner/test-repo/pull/42",
      "score": 1.0,
      "reference": "PR #42 - HIGH risk, Analysis ID: analysis-uuid"
    }
  ]
}
```

---

## Demo Walkthrough Checklist

- [ ] Run Alembic database upgrade migrations successfully.
- [ ] Execute `verify_foundry.py` and receive all success checkmarks.
- [ ] Deploy backend locally via Uvicorn.
- [ ] Submit mock GitHub pull request webhook payload.
- [ ] Fetch Dashboard statistics and confirm risk score updates.
- [ ] Post ingestion request to refresh local snapshots.
- [ ] Retrieve grounded Q&A answering with 100% correct citations.

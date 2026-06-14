# Microsoft Foundry IQ Integration Architecture (Compatibility Mode)

This document describes the design, setup, and execution flows of the Microsoft Foundry IQ intelligence layer in PRPilot under Compatibility Mode.

## Overview

To guarantee compatibility in Azure AI Foundry regions where Agents and File Search tools are unavailable (such as **Central India**), PRPilot uses a database-grounded local prompt context approach. Grounding context is compiled directly from the synchronized PostgreSQL database records and provided to the Azure OpenAI chat completions model.

```mermaid
sequenceDiagram
    participant Client as User / Demo Consumer
    participant API as intelligence API Router
    participant Service as FoundryIQService
    participant Snapshot as Local JSON Snapshot
    participant AIProject as Azure AI Project Client
    participant DB as PostgreSQL
    participant model as Azure OpenAI GPT Model

    rect rgb(240, 248, 255)
        Note over Client, DB: Manual Ingestion Flow (POST /intelligence/ingest)
        Client->>API: trigger ingestion request
        API->>Service: ingest_database()
        Service->>DB: Fetch repos, PRs, and analyses
        DB-->>Service: SQL records
        Service->>Service: Format records as JSON structure
        Service->>Snapshot: Persist prpilot_knowledge_snapshot.json locally
        Service-->>API: Response payload (counts and status)
        API-->>Client: 200 OK (Ingest Statistics)
    end

    rect rgb(255, 240, 245)
        Note over Client, model: Grounded Query Flow (GET /intelligence/query?query=...)
        Client->>API: query query string
        API->>Service: query_knowledge(query)
        Service->>Snapshot: Load local JSON snapshot
        Service->>Service: Build Markdown grounding context and citation map
        Service->>AIProject: Retrieve authenticated AzureOpenAI client
        Service->>model: Submit grounded prompt (JSON mode)
        model-->>Service: Return JSON answer + citation IDs
        Service->>Service: Map citation IDs to full citation records
        Service-->>API: GroundedQueryResponse
        API-->>Client: 200 OK (Answer + Citations)
    end
```

## Database Grounding (Local Snapshot)

Rather than uploading files to Azure vector stores or setting up complex search index pipelines:
1. The ingestion endpoint queries the local PostgreSQL database to retrieve all repositories, pull requests, and latest risk analyses.
2. It compiles this information into a structured JSON knowledge base.
3. The snapshot is saved to the local runtime environment (`tempfile.gettempdir()`) as `prpilot_knowledge_snapshot.json`.

## Grounded Retrieval & Citation Mapping

* **Prompt Construction**: Upon querying, the service reads the JSON snapshot, builds a clean structured Markdown description of the data, and assigns a strict citation ID (e.g. `repo_1`, `pr_1_12`) to each entity.
* **Model Inference**: The query is submitted to Azure OpenAI using the `openai_client.chat.completions.create` API with `response_format={"type": "json_object"}`. The system instructions guide the model to answer using *only* the grounding text and cite references using the designated IDs.
* **Graceful Failure**: If the local snapshot has not yet been initialized via ingestion, the service raises a `PRPilotError`, returning a clean HTTP error to the client.
* **Citations Attributions**: The service receives citation IDs back from the model, validates them against the citation registry, appends the repository name, pull request number, and risk levels, and returns the response.

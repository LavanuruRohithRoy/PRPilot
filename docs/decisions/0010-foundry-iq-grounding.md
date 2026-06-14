# ADR 0010: Agentless Grounding via Database Local Snapshots (Compatibility Mode)

## Status
Accepted

## Context
During deployment testing, we discovered that the Azure AI Foundry resources in the **Central India** region do not support Agent APIs, Vector Stores, or File Search tools. To ensure seamless deployment and full compatibility, we must avoid dependencies on these Agent-specific APIs while maintaining the core query grounding capability.

## Decisions

1. **Remove Agent Framework Dependencies**: We removed all references to Agent creation, threads, runs, vector store files, and managed indexes.
2. **Local Database Grounding**: The ingestion step (`POST /api/v1/intelligence/ingest`) compiles repositories, pull requests, and latest analyses into a local JSON knowledge snapshot (`prpilot_knowledge_snapshot.json`) saved in system temporary storage.
3. **Prompt-based RAG**: During retrieval (`GET /api/v1/intelligence/query`), the local JSON snapshot is loaded, formatted into a structured Markdown document, and passed to a standard Azure OpenAI GPT-4o model deployment through the `AIProjectClient.inference` client.
4. **Strict Reference-ID Citation Mapping**: In the system instructions, the model is given strict, pre-allocated citation keys (e.g. `repo_1`, `pr_1_5`) and required to output replies as a JSON object containing its answer and used citation keys. This completely prevents citation hallucinations, as the service maps these pre-allocated keys directly back to authenticated database records.
5. **AnyIO Thread Pool Execution**: Because the project client SDK calls are synchronous, all Azure client completions are executed inside thread pools using `anyio.to_thread.run_sync`.

## Consequences
* **Region Compatibility**: Full compliance and operational reliability in Central India and other regions lacking Agent support.
* **Cost & Performance**: Bypassing Azure Vector Search reduces runtime service costs and removes remote file upload latency.
* **Accuracy**: Storing pre-allocated citation keys inside the system prompt and matching model outputs to the valid registry guarantees 100% accurate, non-hallucinated citations.

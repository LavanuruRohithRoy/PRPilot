import json
import os
import re
import tempfile
from datetime import UTC, datetime
from typing import Any, cast

from anyio import to_thread
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import PRPilotError
from app.models.pull_request import PullRequest
from app.models.repository import Repository


class FoundryIQService:
    """Service using Azure AI Projects SDK to execute direct grounded completions.

    Eliminates dependencies on Azure Agents, Vector Stores, and File Search.
    """

    SNAPSHOT_PATH = os.path.join(
        tempfile.gettempdir(), "prpilot_knowledge_snapshot.json"
    )

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _get_project_client(self) -> AIProjectClient:
        """Instantiate the AIProjectClient using configured credentials."""
        if not settings.AZURE_AI_FOUNDRY_CONNECTION_STRING:
            raise PRPilotError("AZURE_AI_FOUNDRY_CONNECTION_STRING is not configured.")
        credential = DefaultAzureCredential()
        return AIProjectClient.from_connection_string(  # type: ignore[attr-defined]
            conn_str=settings.AZURE_AI_FOUNDRY_CONNECTION_STRING,
            credential=credential,
        )

    async def ingest_database(self) -> dict[str, Any]:
        """Query active database records and format into a local JSON snapshot."""
        # Query database records
        repo_query = select(Repository).options(
            selectinload(Repository.pull_requests).selectinload(PullRequest.analyses)
        )
        result = await self.session.execute(repo_query)
        repositories = result.scalars().all()

        repo_list = []
        pull_requests_count = 0
        analyses_count = 0

        for repo in repositories:
            pr_list: list[dict[str, Any]] = []
            for pr in repo.pull_requests:
                pull_requests_count += 1
                analyses_list: list[dict[str, Any]] = []
                for a in pr.analyses:
                    analyses_count += 1
                    a_data = {
                        "id": str(a.id),
                        "status": a.status.value if a.status else "pending",
                        "risk_score": a.risk_score,
                        "risk_level": (a.risk_level.value if a.risk_level else "LOW"),
                        "findings": a.findings or [],
                        "summary": a.summary,
                        "created_at": (
                            a.created_at.isoformat() if a.created_at else None
                        ),
                    }
                    analyses_list.append(a_data)
                pr_data = {
                    "id": str(pr.id),
                    "pr_number": pr.pr_number,
                    "title": pr.title,
                    "author": pr.author,
                    "status": pr.status.value if pr.status else "open",
                    "opened_at": (pr.opened_at.isoformat() if pr.opened_at else None),
                    "closed_at": (pr.closed_at.isoformat() if pr.closed_at else None),
                    "analyses": analyses_list,
                }
                pr_list.append(pr_data)
            repo_data = {
                "id": str(repo.id),
                "owner": repo.owner,
                "name": repo.name,
                "full_name": repo.full_name,
                "is_active": repo.is_active,
                "pull_requests": pr_list,
            }
            repo_list.append(repo_data)

        snapshot = {
            "repositories": repo_list,
            "metadata": {
                "exported_at": datetime.now(UTC).isoformat(),
                "repositories_count": len(repositories),
                "pull_requests_count": pull_requests_count,
                "analyses_count": analyses_count,
            },
        }

        # Write snapshot file
        try:
            with open(self.SNAPSHOT_PATH, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
        except Exception as e:
            raise PRPilotError(
                f"Failed to write local knowledge snapshot: {e!s}"
            ) from e

        return {
            "repositories": len(repositories),
            "pull_requests": pull_requests_count,
            "analyses": analyses_count,
            "status": "knowledge_refreshed",
        }

    async def query_knowledge(self, query_str: str) -> dict[str, Any]:
        """Query Azure OpenAI model using local grounding snapshots."""
        if not os.path.exists(self.SNAPSHOT_PATH):
            raise PRPilotError(
                "No grounding knowledge snapshot found. Please run ingestion first."
            )

        try:
            with open(self.SNAPSHOT_PATH, encoding="utf-8") as f:
                snapshot = json.load(f)
        except Exception as e:
            raise PRPilotError(f"Failed to load knowledge snapshot: {e!s}") from e

        # Construct grounded context lines and citations registry
        repositories = snapshot.get("repositories", [])
        context_lines = []
        valid_citations = {}

        for idx, repo in enumerate(repositories):
            repo_ref = f"repo_{idx + 1}"
            valid_citations[repo_ref] = {
                "id": repo_ref,
                "title": repo["full_name"],
                "url": (
                    f"{settings.GITHUB_API_URL}/{repo['full_name']}"
                    if settings.GITHUB_API_URL
                    else None
                ),
                "reference": f"Repository {repo['full_name']}",
            }
            context_lines.append(f"[{repo_ref}] Repository: {repo['full_name']}")
            context_lines.append(
                f"Owner: {repo['owner']}, Name: {repo['name']}, "
                f"Active: {repo['is_active']}"
            )

            for pr in repo.get("pull_requests", []):
                pr_ref = f"pr_{idx + 1}_{pr['pr_number']}"
                completed_analyses = [
                    a for a in pr.get("analyses", []) if a["status"] == "completed"
                ]
                risk_level = "None"
                risk_score = "None"
                findings_str = "None"
                analysis_summary = "None"
                analysis_ref_str = ""

                if completed_analyses:
                    latest = max(
                        completed_analyses,
                        key=lambda x: x.get("created_at") or "",
                    )
                    risk_level = latest.get("risk_level", "LOW")
                    risk_score = str(latest.get("risk_score", 0))
                    if latest.get("findings"):
                        findings_str = ", ".join(latest["findings"])
                    analysis_summary = latest.get("summary") or "None"
                    analysis_ref_str = f", Analysis ID: {latest['id']}"

                title_str = (
                    f"PR #{pr['pr_number']} ({repo['full_name']}) - "
                    f"Risk Level: {risk_level}"
                )
                valid_citations[pr_ref] = {
                    "id": pr_ref,
                    "title": title_str,
                    "url": (
                        f"{settings.GITHUB_API_URL}/{repo['full_name']}/pull/{pr['pr_number']}"
                        if settings.GITHUB_API_URL
                        else None
                    ),
                    "reference": (
                        f"PR #{pr['pr_number']} - {risk_level} risk{analysis_ref_str}"
                    ),
                }

                context_lines.append(
                    f"  [{pr_ref}] Pull Request #{pr['pr_number']}: {pr['title']}"
                )
                context_lines.append(
                    f"    Author: {pr['author']}, Status: {pr['status']}"
                )
                context_lines.append(
                    f"    Risk Score: {risk_score}, Risk Level: {risk_level}"
                )
                context_lines.append(f"    Findings: {findings_str}")
                context_lines.append(f"    Summary: {analysis_summary}")
            context_lines.append("")

        context_text = "\n".join(context_lines)

        def _run_grounded_rag() -> dict[str, Any]:
            use_key_auth = (
                isinstance(settings.AZURE_OPENAI_API_KEY, str)
                and settings.AZURE_OPENAI_API_KEY != ""
                and isinstance(settings.AZURE_OPENAI_ENDPOINT, str)
                and settings.AZURE_OPENAI_ENDPOINT != ""
            )
            if use_key_auth:
                openai_client = AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_version="2024-06-01",
                )
            else:
                project_client = cast(Any, self._get_project_client())
                openai_client = project_client.inference.get_azure_openai_client()

            system_prompt = (
                "You are a helpful PRPilot assistant. Your goal is to answer queries "
                "about the repositories, pull requests, and risk analyses in "
                "the system using only the provided grounding context.\n\n"
                "Grounding Context:\n"
                f"{context_text}\n\n"
                "Instructions:\n"
                "1. Answer the query based strictly on the provided Grounding Context. "
                "If the context does not contain the necessary information, state: "
                "'I cannot answer this question as the required information is not "
                "available in the grounding database.' Do not use external knowledge.\n"
                "2. When you reference a repository or pull request, you MUST cite it "
                "using the matching source identifier in brackets (e.g. [repo_1] or "
                "[pr_1_12]).\n"
                "3. You MUST format your response as a JSON object with two fields:\n"
                "   - 'answer': A detailed, textual explanation of the answer, "
                "including inline bracketed citations (e.g. '[repo_1]').\n"
                "   - 'citation_ids': A list of the citation identifier strings "
                "(e.g. ['repo_1', 'pr_1_12']) that you used in your answer.\n"
                "4. Do not include any formatting other than raw JSON "
                "(do not wrap in markdown code blocks like ```json ... ```)."
            )

            try:
                response = openai_client.chat.completions.create(
                    model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query_str},
                    ],
                    response_format={"type": "json_object"},
                    timeout=30.0,
                )
            except Exception as e:
                raise PRPilotError(
                    f"Azure OpenAI completion request failed: {e!s}"
                ) from e

            response_text = response.choices[0].message.content or "{}"

            # Clean potential Markdown wrap
            raw_text = response_text.strip()
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()

            try:
                res_data = json.loads(raw_text)
            except Exception as e:
                raise PRPilotError(
                    "Failed to parse model response as JSON: "
                    f"{e!s}. Response: {response_text}"
                ) from e

            answer = res_data.get("answer", "")
            citation_ids = res_data.get("citation_ids", [])

            # Extract bracketed citation IDs from answer text as a fallback safety
            extracted_cids = re.findall(r"\[([a-zA-Z0-9_-]+)\]", answer)
            combined_ids = list(set(citation_ids + extracted_cids))

            citations = []
            for cid in combined_ids:
                if cid in valid_citations:
                    ref_info = valid_citations[cid]
                    citations.append(
                        {
                            "id": ref_info["id"],
                            "title": ref_info["title"],
                            "url": ref_info["url"],
                            "score": 1.0,
                            "reference": ref_info["reference"],
                        }
                    )

            return {
                "query": query_str,
                "answer": answer,
                "citations": citations,
            }

        return await to_thread.run_sync(_run_grounded_rag)

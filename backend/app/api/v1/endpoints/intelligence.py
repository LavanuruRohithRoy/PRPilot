from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_foundry_iq_service
from app.schemas.intelligence import GroundedQueryResponse
from app.services.foundry_iq import FoundryIQService

router = APIRouter()


@router.post(
    "/ingest",
    responses={
        200: {
            "description": (
                "Database records successfully ingested into local snapshot."
            ),
            "content": {
                "application/json": {
                    "example": {
                        "repositories": 5,
                        "pull_requests": 24,
                        "analyses": 24,
                        "status": "knowledge_refreshed",
                    }
                }
            },
        }
    },
)
async def ingest_database(
    service: FoundryIQService = Depends(get_foundry_iq_service),
) -> Any:
    """Scan the database, generate structured grounding records,
    and save snapshot locally.
    """
    return await service.ingest_database()


@router.get(
    "/query",
    response_model=GroundedQueryResponse,
    responses={
        200: {
            "description": "Grounded response retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "query": (
                            "Which repositories currently contain "
                            "high-risk pull requests?"
                        ),
                        "answer": (
                            "Based on the analyzed reports, the repository "
                            "'test-owner/test-repo' contains one high-risk "
                            "pull request (#1), which was flagged for "
                            "containing WIP markers and "
                            "missing closed dates [source_1]."
                        ),
                        "citations": [
                            {
                                "id": "pr_1_1",
                                "title": (
                                    "PR #1 (test-owner/test-repo) - Risk Level: HIGH"
                                ),
                                "url": (
                                    "https://api.github.com/test-owner/test-repo/pull/1"
                                ),
                                "score": 1.0,
                                "reference": (
                                    "PR #1 - HIGH risk, Analysis ID: 1234abcd"
                                ),
                            }
                        ],
                    }
                }
            },
        }
    },
)
async def query_intelligence(
    query: str,
    service: FoundryIQService = Depends(get_foundry_iq_service),
) -> Any:
    """Query the Azure OpenAI service using grounded local database context."""
    return await service.query_knowledge(query)

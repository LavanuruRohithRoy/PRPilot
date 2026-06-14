import json
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_foundry_iq_service
from app.core.exceptions import PRPilotError
from app.main import app
from app.models.analysis import Analysis
from app.models.enums import AnalysisStatus, PullRequestStatus, RiskLevel
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.services.foundry_iq import FoundryIQService


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.asyncio
async def test_foundry_iq_service_ingest_empty() -> None:
    # Test service when database has no records
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    service = FoundryIQService(mock_session)
    with patch("builtins.open", mock_open()), patch("json.dump"):
        result = await service.ingest_database()

    assert result["status"] == "knowledge_refreshed"
    assert result["repositories"] == 0
    assert result["pull_requests"] == 0
    assert result["analyses"] == 0


@pytest.mark.asyncio
async def test_foundry_iq_service_ingest_success() -> None:
    mock_session = AsyncMock()
    mock_result = MagicMock()

    # Mock models
    repo = Repository(
        id=uuid.uuid4(),
        owner="owner",
        name="repo",
        full_name="owner/repo",
        is_active=True,
    )
    pr = PullRequest(
        id=uuid.uuid4(),
        repository_id=repo.id,
        pr_number=1,
        title="Test PR",
        author="author",
        status=PullRequestStatus.OPEN,
        opened_at=datetime.now(UTC),
    )
    analysis = Analysis(
        id=uuid.uuid4(),
        pull_request_id=pr.id,
        status=AnalysisStatus.COMPLETED,
        risk_score=20,
        risk_level=RiskLevel.LOW,
        findings=["PR title is extremely short"],
        summary="Summary details",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    pr.analyses = [analysis]
    repo.pull_requests = [pr]

    mock_result.scalars.return_value.all.return_value = [repo]
    mock_session.execute.return_value = mock_result

    service = FoundryIQService(mock_session)
    with patch("builtins.open", mock_open()), patch("json.dump"):
        result = await service.ingest_database()

    assert result["status"] == "knowledge_refreshed"
    assert result["repositories"] == 1
    assert result["pull_requests"] == 1
    assert result["analyses"] == 1


@pytest.mark.asyncio
@patch("app.services.foundry_iq.AIProjectClient")
@patch("app.services.foundry_iq.settings")
async def test_foundry_iq_service_query_success(
    mock_settings: MagicMock,
    mock_client_class: MagicMock,
) -> None:
    mock_settings.AZURE_AI_FOUNDRY_CONNECTION_STRING = "mock-connection-string"
    mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o"
    mock_settings.GITHUB_API_URL = "https://api.github.com"

    mock_session = AsyncMock()
    service = FoundryIQService(mock_session)

    # Mock the snapshot existence and content
    mock_snapshot = {
        "repositories": [
            {
                "id": "repo-id-123",
                "owner": "owner",
                "name": "repo",
                "full_name": "owner/repo",
                "is_active": True,
                "pull_requests": [
                    {
                        "id": "pr-id-456",
                        "pr_number": 1,
                        "title": "Test PR",
                        "author": "author",
                        "status": "open",
                        "opened_at": "2026-06-14T00:00:00Z",
                        "closed_at": None,
                        "analyses": [
                            {
                                "id": "analysis-id-789",
                                "status": "completed",
                                "risk_score": 20,
                                "risk_level": "LOW",
                                "findings": ["PR title is extremely short"],
                                "summary": "Summary details",
                                "created_at": "2026-06-14T00:00:00Z",
                            }
                        ],
                    }
                ],
            }
        ]
    }

    # Mock os.path.exists and builtins.open
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_snapshot))),
    ):
        # Mock Azure project client inference completions
        mock_client = MagicMock()
        mock_client_class.from_connection_string.return_value = mock_client

        mock_openai_client = MagicMock()
        mock_client.inference.get_azure_openai_client.return_value = mock_openai_client

        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps(
            {"answer": "This is a low-risk PR [pr_1_1].", "citation_ids": ["pr_1_1"]}
        )
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_openai_client.chat.completions.create.return_value = mock_completion

        result = await service.query_knowledge(
            "Which repositories contain low risk PRs?"
        )

    assert result["query"] == "Which repositories contain low risk PRs?"
    assert "This is a low-risk PR" in result["answer"]
    assert len(result["citations"]) == 1
    assert result["citations"][0]["id"] == "pr_1_1"
    assert result["citations"][0]["title"] == "PR #1 (owner/repo) - Risk Level: LOW"


@pytest.mark.asyncio
async def test_foundry_iq_service_query_missing_snapshot() -> None:
    mock_session = AsyncMock()
    service = FoundryIQService(mock_session)

    with patch("os.path.exists", return_value=False):
        with pytest.raises(PRPilotError) as exc_info:
            await service.query_knowledge("test query")

    assert "No grounding knowledge snapshot found" in str(exc_info.value)


def test_query_intelligence_api_success(client: TestClient) -> None:
    mock_service = AsyncMock()

    citation = {
        "id": "pr_1_1",
        "title": "PR #1 (owner/repo) - Risk Level: LOW",
        "url": "https://api.github.com/owner/repo/pull/1",
        "score": 1.0,
        "reference": "PR #1 - LOW risk",
    }

    mock_service.query_knowledge.return_value = {
        "query": "Which repositories currently contain high-risk pull requests?",
        "answer": "None, only low risk ones are available.",
        "citations": [citation],
    }

    app.dependency_overrides[get_foundry_iq_service] = lambda: mock_service

    response = client.get("/api/v1/intelligence/query?query=some-query")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == (
        "Which repositories currently contain high-risk pull requests?"
    )
    assert data["answer"] == "None, only low risk ones are available."
    assert len(data["citations"]) == 1
    assert data["citations"][0]["id"] == "pr_1_1"
    assert data["citations"][0]["reference"] == "PR #1 - LOW risk"

    mock_service.query_knowledge.assert_called_once_with("some-query")
    app.dependency_overrides.clear()


def test_ingest_intelligence_api_success(client: TestClient) -> None:
    mock_service = AsyncMock()
    mock_service.ingest_database.return_value = {
        "repositories": 5,
        "pull_requests": 24,
        "analyses": 24,
        "status": "knowledge_refreshed",
    }

    app.dependency_overrides[get_foundry_iq_service] = lambda: mock_service

    response = client.post("/api/v1/intelligence/ingest")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "knowledge_refreshed"
    assert data["repositories"] == 5
    assert data["pull_requests"] == 24
    assert data["analyses"] == 24

    mock_service.ingest_database.assert_called_once()
    app.dependency_overrides.clear()

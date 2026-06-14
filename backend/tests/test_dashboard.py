import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_dashboard_service
from app.main import app
from app.models.enums import AnalysisStatus, RiskLevel
from app.schemas.dashboard import DashboardRecentAnalysis, DashboardSummary


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_get_dashboard_api_success(client: TestClient) -> None:
    mock_service = AsyncMock()

    recent = DashboardRecentAnalysis(
        id=uuid.uuid4(),
        pull_request_id=uuid.uuid4(),
        pr_title="Some PR title",
        pr_number=101,
        repository_name="owner/repo",
        risk_score=45,
        risk_level=RiskLevel.MEDIUM,
        status=AnalysisStatus.COMPLETED,
        created_at=datetime.now(UTC),
    )

    summary = DashboardSummary(
        repositories=4,
        pull_requests=17,
        analyses=17,
        high_risk=3,
        medium_risk=9,
        low_risk=5,
        recent_analyses=[recent],
    )
    mock_service.get_dashboard_summary.return_value = summary

    app.dependency_overrides[get_dashboard_service] = lambda: mock_service

    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()

    assert data["repositories"] == 4
    assert data["pull_requests"] == 17
    assert data["analyses"] == 17
    assert data["high_risk"] == 3
    assert data["medium_risk"] == 9
    assert data["low_risk"] == 5
    assert len(data["recent_analyses"]) == 1
    assert data["recent_analyses"][0]["pr_title"] == "Some PR title"
    assert data["recent_analyses"][0]["risk_level"] == "MEDIUM"

    mock_service.get_dashboard_summary.assert_called_once()
    app.dependency_overrides.clear()

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import (
    get_analysis_repository,
    get_analysis_service,
    get_pull_request_repository,
)
from app.core.exceptions import EntityNotFoundError
from app.main import app
from app.models.analysis import Analysis
from app.models.enums import AnalysisStatus, RiskLevel


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_trigger_analysis_api_success(client: TestClient) -> None:
    mock_service = AsyncMock()
    pr_id = uuid.uuid4()
    analysis = Analysis(
        id=uuid.uuid4(),
        pull_request_id=pr_id,
        status=AnalysisStatus.COMPLETED,
        risk_score=20,
        risk_level=RiskLevel.LOW,
        findings=["PR title is extremely short"],
        summary="Low risk summary",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_service.trigger_analysis.return_value = analysis

    app.dependency_overrides[get_analysis_service] = lambda: mock_service

    response = client.post(f"/api/v1/analyses/run/{pr_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(analysis.id)
    assert data["risk_score"] == 20
    assert data["risk_level"] == "LOW"
    assert data["findings"] == ["PR title is extremely short"]

    mock_service.trigger_analysis.assert_called_once_with(pr_id)
    app.dependency_overrides.clear()


def test_trigger_analysis_api_not_found(client: TestClient) -> None:
    mock_service = AsyncMock()
    pr_id = uuid.uuid4()
    mock_service.trigger_analysis.side_effect = EntityNotFoundError(
        f"Pull Request with ID {pr_id} not found."
    )

    app.dependency_overrides[get_analysis_service] = lambda: mock_service

    response = client.post(f"/api/v1/analyses/run/{pr_id}")
    assert response.status_code == 404
    assert "ENTITY_NOT_FOUND" in response.json()["code"]

    app.dependency_overrides.clear()


def test_get_analysis_api_success(client: TestClient) -> None:
    mock_service = AsyncMock()
    analysis_id = uuid.uuid4()
    analysis = Analysis(
        id=analysis_id,
        pull_request_id=uuid.uuid4(),
        status=AnalysisStatus.COMPLETED,
        risk_score=75,
        risk_level=RiskLevel.HIGH,
        findings=["PR marked as WIP"],
        summary="High risk summary",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_service.get_analysis_status.return_value = analysis

    app.dependency_overrides[get_analysis_service] = lambda: mock_service

    response = client.get(f"/api/v1/analyses/{analysis_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(analysis_id)
    assert data["risk_score"] == 75
    assert data["risk_level"] == "HIGH"
    assert data["findings"] == ["PR marked as WIP"]

    mock_service.get_analysis_status.assert_called_once_with(analysis_id)
    app.dependency_overrides.clear()


def test_list_pull_request_analyses_api(client: TestClient) -> None:
    mock_pr_repo = AsyncMock()
    mock_analysis_repo = AsyncMock()

    pr_id = uuid.uuid4()
    mock_pr_repo.get_by_id.return_value = True  # Mock PR exists
    analysis = Analysis(
        id=uuid.uuid4(),
        pull_request_id=pr_id,
        status=AnalysisStatus.COMPLETED,
        risk_score=35,
        risk_level=RiskLevel.MEDIUM,
        findings=["Some findings"],
        summary="Medium risk summary",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_analysis_repo.list_by_pull_request.return_value = [analysis]

    app.dependency_overrides[get_pull_request_repository] = lambda: mock_pr_repo
    app.dependency_overrides[get_analysis_repository] = lambda: mock_analysis_repo

    response = client.get(f"/api/v1/pull-requests/{pr_id}/analyses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["risk_level"] == "MEDIUM"

    mock_pr_repo.get_by_id.assert_called_once_with(pr_id)
    mock_analysis_repo.list_by_pull_request.assert_called_once_with(pr_id)
    app.dependency_overrides.clear()

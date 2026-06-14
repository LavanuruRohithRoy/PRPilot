import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import EntityNotFoundError
from app.models.analysis import Analysis
from app.models.enums import AnalysisStatus, PullRequestStatus, RiskLevel
from app.models.pull_request import PullRequest
from app.services.analysis_engine import AnalysisEngine
from app.services.analysis_service import AnalysisService


@pytest.mark.asyncio
async def test_analysis_service_trigger_success() -> None:
    mock_analysis_repo = AsyncMock()
    mock_pr_repo = AsyncMock()
    mock_session = AsyncMock()
    mock_engine = AnalysisEngine()

    pr_id = uuid.uuid4()
    pr = PullRequest(
        id=pr_id,
        title="WIP: draft pr",
        status=PullRequestStatus.OPEN,
        opened_at=datetime.now(UTC),
    )
    mock_pr_repo.get_by_id.return_value = pr

    analysis_id = uuid.uuid4()
    analysis = Analysis(
        id=analysis_id,
        pull_request_id=pr_id,
        status=AnalysisStatus.COMPLETED,
        risk_score=20,
        risk_level=RiskLevel.LOW,
        findings=["PR is marked as Work In Progress (WIP) or Draft"],
        summary="Summary test",
    )
    mock_analysis_repo.create.return_value = analysis

    service = AnalysisService(
        analysis_repo=mock_analysis_repo,
        pull_request_repo=mock_pr_repo,
        session=mock_session,
        engine=mock_engine,
    )

    result = await service.trigger_analysis(pr_id)

    assert result == analysis
    mock_pr_repo.get_by_id.assert_called_once_with(pr_id)
    mock_analysis_repo.create.assert_called_once_with(
        pull_request_id=pr_id,
        status=AnalysisStatus.COMPLETED,
        summary=(
            "Analysis completed with risk level LOW (Score: 20/100).\n"
            "Findings:\n"
            "- PR is marked as Work In Progress (WIP) or Draft"
        ),
        risk_score=20,
        risk_level=RiskLevel.LOW,
        findings=["PR is marked as Work In Progress (WIP) or Draft"],
    )
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(analysis)


@pytest.mark.asyncio
async def test_analysis_service_trigger_not_found() -> None:
    mock_analysis_repo = AsyncMock()
    mock_pr_repo = AsyncMock()
    mock_session = AsyncMock()
    mock_engine = AnalysisEngine()

    mock_pr_repo.get_by_id.return_value = None

    service = AnalysisService(
        analysis_repo=mock_analysis_repo,
        pull_request_repo=mock_pr_repo,
        session=mock_session,
        engine=mock_engine,
    )

    pr_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundError) as excinfo:
        await service.trigger_analysis(pr_id)

    assert f"Pull Request with ID {pr_id} not found" in str(excinfo.value)
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_analysis_service_get_status_success() -> None:
    mock_analysis_repo = AsyncMock()
    mock_pr_repo = AsyncMock()
    mock_session = AsyncMock()
    mock_engine = AnalysisEngine()

    analysis_id = uuid.uuid4()
    analysis = Analysis(
        id=analysis_id,
        pull_request_id=uuid.uuid4(),
        status=AnalysisStatus.COMPLETED,
        risk_score=0,
        risk_level=RiskLevel.LOW,
        findings=[],
        summary="Summary test",
    )
    mock_analysis_repo.get_by_id.return_value = analysis

    service = AnalysisService(
        analysis_repo=mock_analysis_repo,
        pull_request_repo=mock_pr_repo,
        session=mock_session,
        engine=mock_engine,
    )

    result = await service.get_analysis_status(analysis_id)

    assert result == analysis
    mock_analysis_repo.get_by_id.assert_called_once_with(analysis_id)


@pytest.mark.asyncio
async def test_analysis_service_get_status_not_found() -> None:
    mock_analysis_repo = AsyncMock()
    mock_pr_repo = AsyncMock()
    mock_session = AsyncMock()
    mock_engine = AnalysisEngine()

    mock_analysis_repo.get_by_id.return_value = None

    service = AnalysisService(
        analysis_repo=mock_analysis_repo,
        pull_request_repo=mock_pr_repo,
        session=mock_session,
        engine=mock_engine,
    )

    analysis_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundError) as excinfo:
        await service.get_analysis_status(analysis_id)

    assert f"Analysis with ID {analysis_id} not found" in str(excinfo.value)

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import (
    get_db_session,
    get_pull_request_repository,
    get_repository_repository,
)
from app.main import app
from app.models.enums import PullRequestStatus
from app.models.pull_request import PullRequest
from app.models.repository import Repository


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_list_repositories(client: TestClient) -> None:
    mock_repo_repository = AsyncMock()

    # Create mock Repository objects
    repo1 = Repository(
        id=uuid.uuid4(),
        owner="owner1",
        name="repo1",
        full_name="owner1/repo1",
        is_active=True,
        created_at=datetime(2026, 6, 14, 12, 0, 0, tzinfo=UTC),
        updated_at=datetime(2026, 6, 14, 12, 0, 0, tzinfo=UTC),
    )
    repo2 = Repository(
        id=uuid.uuid4(),
        owner="owner2",
        name="repo2",
        full_name="owner2/repo2",
        is_active=True,
        created_at=datetime(2026, 6, 14, 11, 0, 0, tzinfo=UTC),
        updated_at=datetime(2026, 6, 14, 11, 0, 0, tzinfo=UTC),
    )
    # Mock list_all returns sorted by created_at DESC (repo1 then repo2)
    mock_repo_repository.list_all.return_value = [repo1, repo2]

    app.dependency_overrides[get_repository_repository] = lambda: mock_repo_repository

    response = client.get("/api/v1/repositories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["full_name"] == "owner1/repo1"
    assert data[1]["full_name"] == "owner2/repo2"

    mock_repo_repository.list_all.assert_called_once()
    app.dependency_overrides.clear()


def test_get_repository_by_id(client: TestClient) -> None:
    mock_repo_repository = AsyncMock()
    repo_id = uuid.uuid4()
    repo = Repository(
        id=repo_id,
        owner="owner",
        name="repo",
        full_name="owner/repo",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_repo_repository.get_by_id.return_value = repo

    app.dependency_overrides[get_repository_repository] = lambda: mock_repo_repository

    # Test existing
    response = client.get(f"/api/v1/repositories/{repo_id}")
    assert response.status_code == 200
    assert response.json()["full_name"] == "owner/repo"
    mock_repo_repository.get_by_id.assert_called_once_with(repo_id)

    # Test not found
    mock_repo_repository.get_by_id.return_value = None
    response = client.get(f"/api/v1/repositories/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Repository not found."

    app.dependency_overrides.clear()


def test_get_repository_by_name(client: TestClient) -> None:
    mock_repo_repository = AsyncMock()
    repo = Repository(
        id=uuid.uuid4(),
        owner="owner",
        name="repo",
        full_name="owner/repo",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_repo_repository.get_by_full_name.return_value = repo

    app.dependency_overrides[get_repository_repository] = lambda: mock_repo_repository

    # Test existing
    response = client.get("/api/v1/repositories/by-name/owner/repo")
    assert response.status_code == 200
    assert response.json()["full_name"] == "owner/repo"
    mock_repo_repository.get_by_full_name.assert_called_once_with("owner/repo")

    # Test not found
    mock_repo_repository.get_by_full_name.return_value = None
    response = client.get("/api/v1/repositories/by-name/nonexistent/repo")
    assert response.status_code == 404
    assert response.json()["detail"] == "Repository not found."

    app.dependency_overrides.clear()


def test_list_repository_pull_requests(client: TestClient) -> None:
    mock_repo_repository = AsyncMock()
    mock_pr_repository = AsyncMock()

    repo_id = uuid.uuid4()
    repo = Repository(
        id=repo_id,
        owner="owner",
        name="repo",
        full_name="owner/repo",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    pr = PullRequest(
        id=uuid.uuid4(),
        repository_id=repo_id,
        pr_number=1,
        title="Test PR",
        author="author",
        status=PullRequestStatus.OPEN,
        opened_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_repo_repository.get_by_id.return_value = repo
    mock_pr_repository.list_by_repository.return_value = [pr]

    app.dependency_overrides[get_repository_repository] = lambda: mock_repo_repository
    app.dependency_overrides[get_pull_request_repository] = lambda: mock_pr_repository

    # Test existing
    response = client.get(f"/api/v1/repositories/{repo_id}/pull-requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test PR"

    # Test repository not found
    mock_repo_repository.get_by_id.return_value = None
    response = client.get(f"/api/v1/repositories/{uuid.uuid4()}/pull-requests")
    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_get_pull_request_by_id(client: TestClient) -> None:
    mock_pr_repository = AsyncMock()
    pr_id = uuid.uuid4()
    pr = PullRequest(
        id=pr_id,
        repository_id=uuid.uuid4(),
        pr_number=1,
        title="Test PR",
        author="author",
        status=PullRequestStatus.OPEN,
        opened_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_pr_repository.get_by_id.return_value = pr

    app.dependency_overrides[get_pull_request_repository] = lambda: mock_pr_repository

    # Test existing
    response = client.get(f"/api/v1/pull-requests/{pr_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test PR"
    mock_pr_repository.get_by_id.assert_called_once_with(pr_id)

    # Test not found
    mock_pr_repository.get_by_id.return_value = None
    response = client.get(f"/api/v1/pull-requests/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pull request not found."

    app.dependency_overrides.clear()


def test_github_webhook_test_endpoint(client: TestClient) -> None:
    mock_repo_repository = AsyncMock()
    mock_pr_repository = AsyncMock()
    mock_session = AsyncMock()

    repo = Repository(
        id=uuid.uuid4(),
        owner="test-owner",
        name="test-repo",
        full_name="test-owner/test-repo",
        is_active=True,
    )
    pr = PullRequest(
        id=uuid.uuid4(),
        repository_id=repo.id,
        pr_number=1,
        title="Test Pull Request",
        author="test-author",
        status=PullRequestStatus.OPEN,
        opened_at=datetime.now(UTC),
    )

    # Mock get_by_full_name returning None initially to trigger create
    mock_repo_repository.get_by_full_name.return_value = None
    mock_repo_repository.create.return_value = repo

    # Mock get_by_repository_and_number returning None initially to trigger create
    mock_pr_repository.get_by_repository_and_number.return_value = None
    mock_pr_repository.create.return_value = pr

    app.dependency_overrides[get_repository_repository] = lambda: mock_repo_repository
    app.dependency_overrides[get_pull_request_repository] = lambda: mock_pr_repository
    app.dependency_overrides[get_db_session] = lambda: mock_session

    response = client.post("/api/v1/webhooks/github/test")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "synchronized"
    assert data["repository"]["full_name"] == "test-owner/test-repo"
    assert data["pull_request"]["title"] == "Test Pull Request"

    mock_repo_repository.get_by_full_name.assert_called_once_with(
        "test-owner/test-repo"
    )
    mock_repo_repository.create.assert_called_once()
    mock_pr_repository.get_by_repository_and_number.assert_called_once_with(repo.id, 1)
    mock_pr_repository.create.assert_called_once()
    assert mock_session.commit.call_count == 2
    assert mock_session.refresh.call_count == 2

    app.dependency_overrides.clear()

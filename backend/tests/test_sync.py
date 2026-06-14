import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import DomainValidationError
from app.integrations.github.exceptions import (
    GitHubAuthenticationError,
)
from app.integrations.github.mappers import map_pull_request, map_repository
from app.integrations.github.schemas import (
    GitHubPullRequest,
    GitHubRepository,
    GitHubUser,
)
from app.integrations.github.services import GitHubSyncService
from app.models.enums import PullRequestStatus
from app.models.repository import Repository
from app.repositories.repository import RepositoryRepository

# --- Test DTO Mapper Layer ---


def test_map_repository() -> None:
    owner = GitHubUser(
        id=123,
        login="owner-login",
        avatar_url="https://avatar.url",
        html_url="https://html.url/owner",
    )
    dto = GitHubRepository(
        id=456,
        name="repo-name",
        full_name="owner-login/repo-name",
        private=False,
        default_branch="main",
        html_url="https://html.url/repo",
        owner=owner,
    )
    mapped = map_repository(dto)
    assert mapped == {
        "owner": "owner-login",
        "name": "repo-name",
        "full_name": "owner-login/repo-name",
        "is_active": True,
    }


def test_map_pull_request_open() -> None:
    user = GitHubUser(
        id=123,
        login="author-login",
        avatar_url="https://avatar.url",
        html_url="https://html.url/author",
    )
    dto = GitHubPullRequest(
        id=789,
        number=42,
        title="PR Title",
        state="open",
        html_url="https://html.url/pr",
        created_at=datetime(2026, 6, 14, 12, 0, 0, tzinfo=UTC),
        updated_at=datetime(2026, 6, 14, 13, 0, 0, tzinfo=UTC),
        merged_at=None,
        user=user,
    )
    mapped = map_pull_request(dto)
    assert mapped == {
        "pr_number": 42,
        "title": "PR Title",
        "author": "author-login",
        "status": PullRequestStatus.OPEN,
        "opened_at": datetime(2026, 6, 14, 12, 0, 0, tzinfo=UTC),
        "closed_at": None,
    }


def test_map_pull_request_merged() -> None:
    user = GitHubUser(
        id=123,
        login="author-login",
        avatar_url="https://avatar.url",
        html_url="https://html.url/author",
    )
    dto = GitHubPullRequest(
        id=789,
        number=42,
        title="PR Title",
        state="closed",
        html_url="https://html.url/pr",
        created_at=datetime(2026, 6, 14, 12, 0, 0, tzinfo=UTC),
        updated_at=datetime(2026, 6, 14, 13, 0, 0, tzinfo=UTC),
        merged_at=datetime(2026, 6, 14, 13, 0, 0, tzinfo=UTC),
        user=user,
    )
    mapped = map_pull_request(dto)
    assert mapped == {
        "pr_number": 42,
        "title": "PR Title",
        "author": "author-login",
        "status": PullRequestStatus.MERGED,
        "opened_at": datetime(2026, 6, 14, 12, 0, 0, tzinfo=UTC),
        "closed_at": datetime(2026, 6, 14, 13, 0, 0, tzinfo=UTC),
    }


# --- Test Repositories with Mock Session ---


@pytest.mark.asyncio
async def test_repository_repo_get_by_id() -> None:
    mock_session = AsyncMock()
    mock_repo = Repository(
        id=uuid.uuid4(), owner="owner", name="name", full_name="owner/name"
    )
    mock_session.get.return_value = mock_repo

    repo_repository = RepositoryRepository(mock_session)
    result = await repo_repository.get_by_id(mock_repo.id)

    assert result == mock_repo
    mock_session.get.assert_called_once_with(Repository, mock_repo.id)


@pytest.mark.asyncio
async def test_repository_repo_create() -> None:
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    repo_repository = RepositoryRepository(mock_session)
    repo = await repo_repository.create(
        owner="owner", name="name", full_name="owner/name", is_active=True
    )
    assert repo.owner == "owner"
    assert repo.name == "name"
    assert repo.full_name == "owner/name"
    mock_session.add.assert_called_once_with(repo)


# --- Test Service Sync & Orchestration ---


@pytest.mark.asyncio
async def test_sync_repository_new() -> None:
    mock_client = AsyncMock()
    mock_client.get.return_value = {
        "id": 1,
        "name": "name",
        "full_name": "owner/name",
        "private": False,
        "default_branch": "main",
        "html_url": "https://github.com/owner/name",
        "owner": {
            "id": 10,
            "login": "owner",
            "avatar_url": "https://avatar",
            "html_url": "https://github.com/owner",
        },
    }

    mock_repo_repository = AsyncMock()
    mock_repo_repository.get_by_full_name.return_value = None

    repo_instance = Repository(
        id=uuid.uuid4(),
        owner="owner",
        name="name",
        full_name="owner/name",
        is_active=True,
    )
    mock_repo_repository.create.return_value = repo_instance

    mock_pr_repository = AsyncMock()
    mock_session = AsyncMock()

    service = GitHubSyncService(
        client=mock_client,
        repository_repo=mock_repo_repository,
        pull_request_repo=mock_pr_repository,
        session=mock_session,
    )

    result = await service.sync_repository("owner", "name")

    assert result == repo_instance
    mock_client.get.assert_called_once_with("repos/owner/name")
    mock_repo_repository.get_by_full_name.assert_called_once_with("owner/name")
    mock_repo_repository.create.assert_called_once_with(
        owner="owner", name="name", full_name="owner/name", is_active=True
    )
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(repo_instance)


@pytest.mark.asyncio
async def test_sync_repository_exception_translation() -> None:
    mock_client = AsyncMock()
    mock_client.get.side_effect = GitHubAuthenticationError("Auth error")

    mock_repo_repository = AsyncMock()
    mock_pr_repository = AsyncMock()
    mock_session = AsyncMock()

    service = GitHubSyncService(
        client=mock_client,
        repository_repo=mock_repo_repository,
        pull_request_repo=mock_pr_repository,
        session=mock_session,
    )

    with pytest.raises(DomainValidationError) as excinfo:
        await service.sync_repository("owner", "name")

    assert "GitHub authorization failed." in str(excinfo.value)
    mock_session.rollback.assert_called_once()

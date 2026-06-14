import hashlib
import hmac
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_github_sync_service
from app.core.config import settings
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_github_webhook_invalid_signature(client: TestClient) -> None:
    headers = {
        "X-Hub-Signature-256": "sha256=invalid",
        "X-GitHub-Event": "ping",
    }
    response = client.post(
        "/api/v1/webhooks/github",
        json={"zen": "Testing"},
        headers=headers,
    )
    assert response.status_code == 401
    assert "HMAC verification failed" in response.json()["detail"]


def test_github_webhook_ping(client: TestClient) -> None:
    secret = settings.GITHUB_WEBHOOK_SECRET or "testsecret"
    settings.GITHUB_WEBHOOK_SECRET = secret

    payload = b'{"zen": "Testing"}'
    mac = hmac.new(secret.encode("utf-8"), msg=payload, digestmod=hashlib.sha256)
    signature = f"sha256={mac.hexdigest()}"

    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "ping",
    }
    response = client.post(
        "/api/v1/webhooks/github",
        content=payload,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_github_webhook_repository(client: TestClient) -> None:
    mock_sync_service = AsyncMock()
    app.dependency_overrides[get_github_sync_service] = lambda: mock_sync_service

    secret = settings.GITHUB_WEBHOOK_SECRET or "testsecret"
    payload = (
        b'{"action": "created", "repository": {'
        b'"id": 123, "name": "test-repo", "full_name": "owner/test-repo", '
        b'"private": false, "default_branch": "main", '
        b'"html_url": "https://github.com/owner/test-repo", '
        b'"owner": {"id": 10, "login": "owner", '
        b'"avatar_url": "https://avatar", "html_url": "https://github.com/owner"}'
        b"}}"
    )
    mac = hmac.new(secret.encode("utf-8"), msg=payload, digestmod=hashlib.sha256)
    signature = f"sha256={mac.hexdigest()}"

    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "repository",
    }
    response = client.post(
        "/api/v1/webhooks/github",
        content=payload,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {"status": "synchronized"}
    mock_sync_service.sync_repository.assert_called_once_with("owner", "test-repo")

    app.dependency_overrides.clear()

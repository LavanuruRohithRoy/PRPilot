import hashlib
import hmac
import io
import sys

from app.integrations.github.auth import build_github_headers
from app.integrations.github.client import GitHubClient
from app.integrations.github.exceptions import GitHubWebhookVerificationError
from app.integrations.github.webhooks import verify_webhook_signature


def main() -> None:
    # Force stdout to use utf-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    # 1. Verify auth headers generated
    headers = build_github_headers("test-token")
    assert headers["Authorization"] == "Bearer test-token"
    assert headers["Accept"] == "application/vnd.github+json"
    print("✓ auth headers generated")

    # 2 & 3. Verify signature checking
    secret = "webhook-secret-key"
    payload = b'{"action": "opened", "number": 1}'

    # Compute signature
    mac = hmac.new(secret.encode("utf-8"), msg=payload, digestmod=hashlib.sha256)
    valid_signature = f"sha256={mac.hexdigest()}"

    # Test valid signature
    assert verify_webhook_signature(payload, valid_signature, secret) is True
    print("✓ valid signature accepted")

    # Test invalid signature
    try:
        verify_webhook_signature(payload, "sha256=invalid-signature", secret)
        raise AssertionError("Invalid signature was accepted!")
    except GitHubWebhookVerificationError:
        print("✓ invalid signature rejected")

    # 4. Verify client instantiated (without calls)
    client = GitHubClient(api_url="https://api.github.com", token="test-token")
    assert client.api_url == "https://api.github.com"
    assert client.token == "test-token"
    print("✓ client instantiated")


if __name__ == "__main__":
    main()

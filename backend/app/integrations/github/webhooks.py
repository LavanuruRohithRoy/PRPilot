import hashlib
import hmac

from app.integrations.github.exceptions import GitHubWebhookVerificationError


def verify_webhook_signature(
    payload: bytes, signature: str | None, secret: str
) -> bool:
    """Compute and verify HMAC SHA-256 signature against GitHub."""
    if not signature:
        raise GitHubWebhookVerificationError("Missing X-Hub-Signature-256 header.")

    expected_prefix = "sha256="
    if signature.startswith(expected_prefix):
        clean_signature = signature[len(expected_prefix) :]
    else:
        clean_signature = signature

    mac = hmac.new(
        secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    )
    computed_signature = mac.hexdigest()

    if not hmac.compare_digest(computed_signature, clean_signature):
        raise GitHubWebhookVerificationError(
            "HMAC verification failed. Signature mismatch."
        )

    return True

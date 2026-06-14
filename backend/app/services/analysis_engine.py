from datetime import UTC, datetime
from typing import Any

from app.models.enums import AnalysisStatus, PullRequestStatus, RiskLevel
from app.models.pull_request import PullRequest


class AnalysisEngine:
    """Deterministic, rule-based engine to evaluate pull request risk."""

    def analyze(self, pr: PullRequest) -> dict[str, Any]:
        """Analyze a PR against deterministic rules and generate a risk assessment."""
        risk_score = 0
        findings = []

        # 1. WIP/Draft Check
        title_lower = pr.title.lower()
        if "wip" in title_lower or "draft" in title_lower:
            risk_score += 20
            findings.append("PR is marked as Work In Progress (WIP) or Draft")

        # 2. Title Length Checks
        if len(pr.title) > 80:
            risk_score += 10
            findings.append("PR title length exceeds 80 characters")
        elif len(pr.title) < 10:
            risk_score += 15
            findings.append("PR title is extremely short")

        # 3. Stale PR Check (only for Open PRs)
        if pr.status == PullRequestStatus.OPEN:
            now = datetime.now(UTC)
            # Ensure opened_at is timezone-aware
            opened_at = pr.opened_at
            if opened_at.tzinfo is None:
                opened_at = opened_at.replace(tzinfo=UTC)

            age_days = (now - opened_at).days
            if age_days > 30:
                risk_score += 25
                findings.append(
                    f"PR has been open for more than 30 days ({age_days} days)"
                )

        # 4. Missing Closure Date Check
        if pr.status in (PullRequestStatus.CLOSED, PullRequestStatus.MERGED):
            if pr.closed_at is None:
                risk_score += 20
                findings.append(
                    "PR status is closed or merged but closed_at timestamp is missing"
                )

        # Cap the risk score between 0 and 100
        risk_score = max(0, min(100, risk_score))

        # Map score to RiskLevel
        if risk_score <= 30:
            risk_level = RiskLevel.LOW
        elif risk_score <= 70:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH

        # Generate human-readable summary
        if findings:
            findings_text = "\n".join(f"- {f}" for f in findings)
            summary = (
                f"Analysis completed with risk level {risk_level.value} "
                f"(Score: {risk_score}/100).\nFindings:\n{findings_text}"
            )
        else:
            summary = (
                f"Analysis completed with risk level {risk_level.value} "
                f"(Score: {risk_score}/100). No risk findings detected."
            )

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "findings": findings,
            "summary": summary,
            "status": AnalysisStatus.COMPLETED,
        }

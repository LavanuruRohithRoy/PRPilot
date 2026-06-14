from datetime import UTC, datetime, timedelta

from app.models.enums import AnalysisStatus, PullRequestStatus, RiskLevel
from app.models.pull_request import PullRequest
from app.services.analysis_engine import AnalysisEngine


def test_analysis_engine_low_risk() -> None:
    # A standard PR with no warnings
    pr = PullRequest(
        title="Implement features",
        status=PullRequestStatus.OPEN,
        opened_at=datetime.now(UTC),
    )
    engine = AnalysisEngine()
    result = engine.analyze(pr)

    assert result["risk_score"] == 0
    assert result["risk_level"] == RiskLevel.LOW
    assert len(result["findings"]) == 0
    assert "No risk findings detected" in result["summary"]
    assert result["status"] == AnalysisStatus.COMPLETED


def test_analysis_engine_wip_and_short_title() -> None:
    # PR marked as draft/wip and a very short title (< 10 chars)
    pr = PullRequest(
        title="WIP: fix",
        status=PullRequestStatus.OPEN,
        opened_at=datetime.now(UTC),
    )
    engine = AnalysisEngine()
    result = engine.analyze(pr)

    # WIP (+20) + Short title (+15) = 35 -> MEDIUM risk
    assert result["risk_score"] == 35
    assert result["risk_level"] == RiskLevel.MEDIUM
    assert len(result["findings"]) == 2
    assert "PR is marked as Work In Progress (WIP) or Draft" in result["findings"]
    assert "PR title is extremely short" in result["findings"]


def test_analysis_engine_stale_and_long_title() -> None:
    # PR opened > 30 days ago and very long title (> 80 chars)
    long_title = "a" * 85
    opened_at = datetime.now(UTC) - timedelta(days=40)
    pr = PullRequest(
        title=long_title,
        status=PullRequestStatus.OPEN,
        opened_at=opened_at,
    )
    engine = AnalysisEngine()
    result = engine.analyze(pr)

    # Long title (+10) + Stale (+25) = 35 -> MEDIUM risk
    assert result["risk_score"] == 35
    assert result["risk_level"] == RiskLevel.MEDIUM
    assert len(result["findings"]) == 2
    assert "PR title length exceeds 80 characters" in result["findings"]
    assert "PR has been open for more than 30 days" in result["findings"][1]


def test_analysis_engine_merged_not_risky() -> None:
    # A merged PR should not increase the risk score
    pr = PullRequest(
        title="A beautiful PR ready for deployment",
        status=PullRequestStatus.MERGED,
        opened_at=datetime.now(UTC) - timedelta(days=10),
        closed_at=datetime.now(UTC),
    )
    engine = AnalysisEngine()
    result = engine.analyze(pr)

    # Risk score should be 0 because it's merged and has valid closed_at
    assert result["risk_score"] == 0
    assert result["risk_level"] == RiskLevel.LOW


def test_analysis_engine_closed_missing_date() -> None:
    # PR closed but missing closed_at date
    pr = PullRequest(
        title="Some updates",
        status=PullRequestStatus.CLOSED,
        opened_at=datetime.now(UTC) - timedelta(days=5),
        closed_at=None,
    )
    engine = AnalysisEngine()
    result = engine.analyze(pr)

    # Missing closed_at (+20) = 20 -> LOW risk
    assert result["risk_score"] == 20
    assert result["risk_level"] == RiskLevel.LOW
    assert (
        "PR status is closed or merged but closed_at timestamp is missing"
        in result["findings"]
    )

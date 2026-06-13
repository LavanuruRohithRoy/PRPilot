from enum import StrEnum


class AnalysisStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PullRequestStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"

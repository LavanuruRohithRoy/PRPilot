import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import AnalysisStatus, RiskLevel

if TYPE_CHECKING:
    from app.models.pull_request import PullRequest


class Analysis(BaseModel):
    """ORM Model representing an AI analysis run against a pull request snapshot."""

    __tablename__ = "analyses"

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pull_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[AnalysisStatus] = mapped_column(
        SQLAlchemyEnum(AnalysisStatus, native_enum=True),
        default=AnalysisStatus.PENDING,
        nullable=False,
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_score: Mapped[int | None] = mapped_column(nullable=True)
    risk_level: Mapped[RiskLevel | None] = mapped_column(
        SQLAlchemyEnum(RiskLevel, native_enum=True), nullable=True
    )
    findings: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship(
        "PullRequest", back_populates="analyses"
    )

    __table_args__ = (
        CheckConstraint(
            "risk_score >= 0 AND risk_score <= 100", name="chk_analysis_risk_score"
        ),
    )

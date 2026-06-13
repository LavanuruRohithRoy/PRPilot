import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import PullRequestStatus

if TYPE_CHECKING:
    from app.models.analysis import Analysis
    from app.models.repository import Repository


class PullRequest(BaseModel):
    """ORM Model representing a pull request snapshot from the code provider."""

    __tablename__ = "pull_requests"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pr_number: Mapped[int] = mapped_column(index=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[PullRequestStatus] = mapped_column(
        SQLAlchemyEnum(PullRequestStatus, native_enum=True),
        default=PullRequestStatus.OPEN,
        nullable=False,
    )
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="pull_requests"
    )
    analyses: Mapped[list["Analysis"]] = relationship(
        "Analysis",
        back_populates="pull_request",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("repository_id", "pr_number", name="uq_repository_pr_number"),
    )

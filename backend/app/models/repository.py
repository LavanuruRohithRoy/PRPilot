from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.pull_request import PullRequest


class Repository(BaseModel):
    """ORM Model representing a code repository tracked by the platform."""

    __tablename__ = "repositories"

    owner: Mapped[str] = mapped_column(index=True, nullable=False)
    name: Mapped[str] = mapped_column(index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    pull_requests: Mapped[list["PullRequest"]] = relationship(
        "PullRequest",
        back_populates="repository",
        cascade="all, delete-orphan",
    )

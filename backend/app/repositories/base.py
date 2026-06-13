from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository interface defining session ownership and generic typing."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

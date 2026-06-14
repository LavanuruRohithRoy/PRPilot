from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider yielding active database sessions."""
    async for session in get_session():
        yield session

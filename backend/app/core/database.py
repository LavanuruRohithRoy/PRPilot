from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# Create the async engine. settings.DATABASE_URL is a PostgresDsn object,
# so we cast it to str.
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=False,
    future=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency helper to yield a database session for FastAPI routes."""
    async with async_session_maker() as session:
        yield session

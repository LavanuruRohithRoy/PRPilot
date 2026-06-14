from fastapi import FastAPI

from app.api.handlers import register_exception_handlers
from app.api.v1.api import api_router
from app.core.lifespan import lifespan

app = FastAPI(
    title="PRPilot API",
    description="AI-powered Pull Request Intelligence Platform",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


# Register exception handlers
register_exception_handlers(app)

# Register v1 router prefix
app.include_router(api_router, prefix="/api/v1")

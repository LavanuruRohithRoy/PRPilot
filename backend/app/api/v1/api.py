from fastapi import APIRouter

from app.api.v1.endpoints import (
    analysis_runs,
    dashboard,
    intelligence,
    meta,
    pull_requests,
    repositories,
    webhooks,
)

api_router = APIRouter()
api_router.include_router(meta.router, prefix="/meta", tags=["metadata"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(
    repositories.router, prefix="/repositories", tags=["repositories"]
)
api_router.include_router(
    pull_requests.router, prefix="/pull-requests", tags=["pull-requests"]
)
api_router.include_router(analysis_runs.router, prefix="/analyses", tags=["analyses"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(
    intelligence.router, prefix="/intelligence", tags=["intelligence"]
)

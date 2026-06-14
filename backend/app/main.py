from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.handlers import register_exception_handlers
from app.api.v1.api import api_router
from app.core.lifespan import lifespan

app = FastAPI(
    title="PRPilot API",
    description="AI-powered Pull Request Intelligence Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow the Vite dev server and any deployed frontend origin to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


# Register exception handlers
register_exception_handlers(app)

# Register v1 router prefix
app.include_router(api_router, prefix="/api/v1")

from fastapi import FastAPI

app = FastAPI(
    title="PRPilot API",
    description="AI-powered Pull Request Intelligence Platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

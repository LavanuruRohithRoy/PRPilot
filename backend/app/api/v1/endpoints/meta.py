from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_meta() -> dict[str, str]:
    """Expose service metadata information for routing infrastructure validation."""
    return {
        "service": "prpilot",
        "version": "0.1.0",
    }

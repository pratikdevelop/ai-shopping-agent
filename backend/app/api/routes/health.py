"""Health-check endpoint."""

from fastapi import APIRouter

from backend.app.core.config import APP_NAME, APP_VERSION

router = APIRouter(tags=["health"])


@router.get("/api/health", summary="Check API health")
async def get_health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": APP_VERSION,
    }

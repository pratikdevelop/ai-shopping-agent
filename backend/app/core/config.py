"""Environment-backed settings for the FastAPI application."""

from __future__ import annotations

import os

APP_NAME = os.getenv("APP_NAME", "AI Shopping & Deal-Finder API")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()


def get_cors_origins() -> list[str]:
    """Return comma-separated frontend origins, with safe local defaults."""
    raw_origins = os.getenv("CORS_ORIGINS")
    if not raw_origins:
        return ["http://localhost:4200", "http://127.0.0.1:4200"]

    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

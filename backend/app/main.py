"""FastAPI entry point for the AI Shopping & Deal-Finder API."""

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import health, shopping
from backend.app.core.config import APP_NAME, APP_VERSION, get_cors_origins

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Backend API for the AI Shopping & Deal-Finder application. "
        "Shopping searches are executed by the existing LangGraph agent."
    ),
)

# The graph is initialized lazily on the first search, so /api/health remains
# available even when an LLM key or Fleet MCP connection needs configuration.
app.state.shopping_agent = None
app.state.shopping_agent_lock = asyncio.Lock()

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(health.router)
app.include_router(shopping.router, prefix="/api/v1")

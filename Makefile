.PHONY: run dev api test

# Existing interactive CLI for the LangGraph agent.
run:
	uv run --active python cli.py

# Existing LangGraph development server.
dev:
	uv run --active langgraph dev

# FastAPI backend.
api:
	uv run --active uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

# FastAPI backend tests.
test:
	uv run --active pytest backend/tests -q

.PHONY: run dev

run:
	uv run --active python cli.py

dev:
	uv run --active langgraph dev

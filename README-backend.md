# FastAPI backend — Phase 1

This is the first API skeleton for the existing AI Shopping & Deal-Finder project.
It deliberately does **not** invoke LangGraph yet. Search requests are validated and
stored in a temporary in-memory registry, and every response is marked
`mode: "placeholder"`. No retailer data is researched or returned at this stage.

## 1. Install dependencies

From the project root (the directory containing `pyproject.toml`):

```bash
uv lock
uv sync --active
```

This updates both `pyproject.toml` and `uv.lock` using the installed `uv` tool.

## 2. Start the API

```bash
uv run --active uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

- Health: http://127.0.0.1:8000/api/health
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## 3. Try a search request

```bash
curl -X POST http://127.0.0.1:8000/api/v1/shopping/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"Apple iPhone 15 128GB","budget_amount":"80000","city":"Ujjain","state":"Madhya Pradesh"}'
```

Then use the returned `search_id` with:

```text
GET /api/v1/shopping/search/{search_id}
GET /api/v1/shopping/search/{search_id}/deals
```

## 4. Run API tests

```bash
uv run --active pytest backend/tests -q
```

## Important limitations of this phase

- Search records are held in process memory and disappear when the API restarts.
- Search results are placeholders with an empty `deals` list.
- The existing LangGraph agent, Tavily and URL-reading tools are not called yet.
- Do not use placeholder responses to make purchase decisions.

The Angular development origin is allowed by default. Set `CORS_ORIGINS` to a
comma-separated list of exact frontend origins when needed.

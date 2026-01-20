# Backend (FastAPI)

## Run (dev)
1. Create a virtualenv and install dependencies:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Create `.env` from `.env.example` if desired.
3. Start the server:
   - `uvicorn app.main:app --reload --port 8000`

## Health check
- `GET /health` returns `{ "status": "ok" }`

## Practice endpoints (require AI)
These endpoints require Ollama to be running and reachable via `OLLAMA_BASE_URL`.

- `POST /practice/generate`
- `POST /practice/submit`
- `POST /questions/{id}/report`

API docs live under `API_specifications/`.

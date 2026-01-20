# Ollama client (internal)

Code: backend/app/infra/llm/ollama_client.py

## Purpose
- Minimal wrapper for Ollama HTTP calls.
- Centralizes error handling and strict JSON parsing.

## Public API
- `OllamaClient.generate_json(model: str, prompt: str) -> dict`
  - Calls `POST {base_url}/api/generate` with `stream=false`.
  - Parses `response.response` as JSON.

## Errors
- Raises `OllamaUnavailable` when:
  - network errors/timeouts occur
  - HTTP status ≥ 400
  - model returns non-JSON output

## Notes
- Prompting code must ensure the model returns JSON only.

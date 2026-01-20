2026-01-20 16:24:46: Next steps

- AI setup so practice works end-to-end
	- Install/start Ollama locally.
	- Pull models referenced in backend/.env (defaults: `qwen2.5:14b`).
	- If you change models, update `backend/.env` (or environment variables) and re-test `POST /practice/generate` + `POST /practice/submit`.

- E2E “happy path” check (when Ollama is ready)
	- Create a concept.
	- Call `POST /practice/generate` → store `question.id`.
	- Call `POST /practice/submit` with a real answer → verify `attempt`, `progress` updates and `next_due_at` rules.
	- Call `POST /questions/{id}/report` on a real question → verify remove + replacement behavior.

- Frontend scaffolding (currently blocked)
	- Install Node.js + npm (or use a machine where it’s available), then scaffold React (Vite React-TS).
	- Add a minimal UI: concept list/create + “Practice” screen that calls generate/submit.

- Tighten API consistency / ergonomics
	- Add a stable, consistent error schema across all endpoints (right now the shape is similar but not centrally enforced).
	- Consider returning a small “practice session context” from `POST /practice/generate` (e.g., `concept` summary) to simplify the frontend.

- Improve tag continuity persistence
	- Right now `recent_tags` is derived from the last 3 attempts.
	- Add a tiny “recent questions”/“session history” store (YAML) if you want tag continuity even before any attempts exist.

- Tests and dev tooling
	- Keep `pytest` tests growing around higher-risk parts (question bank, report replace logic, YAML atomic writes).
	- Optional: add a short script or Makefile target for `run server`, `run tests`, `run smoke test`.


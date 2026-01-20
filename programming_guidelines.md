## Programming guidelines & project conventions

### Primary goals
- Clarity over cleverness: prefer straightforward, maintainable solutions.
- Keep modules small and responsibilities crisp (avoid “god files”).
- Make behavior explicit and testable (especially scheduling and grading logic).

### API conventions (ALL interfaces)

In this project, “API” includes:
- HTTP endpoints (FastAPI routes)
- Public module/class/function interfaces inside the codebase
- Frontend module APIs (exported functions/components) when they form reusable surfaces

#### General API rules
- Keep APIs simple:
	- Prefer small, stable interfaces.
	- Avoid premature generalization; add parameters only when needed.
	- Prefer explicit inputs over implicit globals.
- Define what is “public” vs “internal”:
	- Public = used across layers/modules (or intended for reuse).
	- Internal = private helpers; keep them local and unexported.

#### In-code API documentation (required)
- Python:
	- Add type hints for all function parameters and return values (including internal helpers when non-trivial).
	- Add docstrings for any public module/class/function, and for any non-obvious internal function.
	- Docstrings must cover:
		- purpose
		- parameters (types, meaning)
		- return value (type, meaning)
		- raised exceptions (when applicable)
		- side effects (file writes, network calls, mutations)
		- important invariants/constraints
- TypeScript/React:
	- Prefer strong TypeScript types for function props/returns.
	- Add JSDoc/TSDoc comments for exported functions/components when intent isn’t obvious or the API is reused.

#### HTTP API conventions (FastAPI)
- Treat endpoints as public APIs:
	- Strong typing via Pydantic models for request/response.
	- Explicit HTTP status codes for success and errors.
	- Validate all inputs; never trust client-provided IDs or timestamps.
	- Do not leak internal storage formats (YAML layouts) into responses unless intentionally part of the contract.
	- Use consistent error shapes across endpoints.

#### API docs in Markdown
- HTTP endpoint specs (required):
	- Each endpoint has a dedicated Markdown file under `API_specifications/`.
	- Must include: purpose, request schema, response schema, examples, and error responses.
- Internal/code API docs (selective, for key surfaces):
	- For important subsystems (e.g., scheduling engine, YAML storage layer, Ollama client, evaluator), add Markdown docs under `API_specifications/internal/`.
	- Keep these short: public functions/classes, inputs/outputs, invariants, and examples.

### Code comments & readability
- APIs: comment thoroughly (docstrings + types) as above.
- Non-API code: comment when intent is not obvious:
	- Scheduling math and mastery/cooldown updates
	- Question selection weighting decisions
	- Evaluator pass/fail criteria and regeneration behavior
- Prefer naming + small functions over excessive inline comments.

### Architecture conventions
- Prefer a clean, layered structure in the backend:
	- API layer (FastAPI routes)
	- Domain layer (scheduling, mastery updates, selection algorithm)
	- Infrastructure layer (YAML storage, Ollama client)
- Avoid cross-layer imports that create cycles.
- Keep the scheduling algorithm and parameters centralized (single module) to avoid drift.

### Documentation conventions
- Architectural decisions belong in `specification.md` under “Architecture decisions”.
- API endpoint docs belong in `API_specifications/`.
- Document any “non-obvious” algorithmic choice with:
	- Why this approach
	- Alternatives considered
	- Tradeoffs
	- How to change it later (parameters / files)

### Testing & quality (guiding principles)
- Write tests for the highest-risk logic first:
	- YAML read/write and atomic saves
	- mastery/cooldown update rules
	- concept selection weighting
	- question bank rules + evaluator gating
- Keep deterministic unit tests (mock time + mock LLM/evaluator responses).

### Style & tooling (recommended)
- Backend:
	- Type hints everywhere; Pydantic models for I/O.
	- Formatting/lint: ruff + black (or ruff-format).
	- Structured logging for API requests and AI calls.
- Frontend:
	- Simple responsive design (mobile + desktop).
	- Keep API client code in one place (single module).
	- Lint/format via eslint + prettier.

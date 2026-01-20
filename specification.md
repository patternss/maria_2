## Purpose

This application is a teaching tool for learning and iterating on new concepts.

Core loop (MVP): a user adds a concept → the assistant generates questions → the user answers → the assistant grades and explains → progress updates → future questions adapt based on progress.


## Project documentation map

- Coding conventions: [programming_guidelines.md](programming_guidelines.md)
- HTTP API docs (one endpoint per file): [API_specifications/README.md](API_specifications/README.md)
- Internal/code API docs (key modules/classes/functions): [API_specifications/internal/README.md](API_specifications/internal/README.md)


## MVP scope

### In scope
- Single-user local mode (no authentication) while keeping the data model expandable to multiple users.
- Concepts with: title (required), optional description, optional tags, optional source link.
- Practice sessions are mixed across concepts (not one concept at a time).
- Question bank per concept (cap 10) with automated quality evaluation and user reporting.
- Progress tracking with mastery/cooldown scheduling and tag/topic continuity.
- AI required for practice (block practice if AI is down).

### Out of scope (for MVP)
- Tasks/exercises (future feature)
- Multi-user accounts (future feature)
- Difficulty levels (we do not explicitly rate question difficulty yet)


## Features (current)

1. Concept input
	- Create and list concepts.
	- Fields: title, description (optional), tags (optional), source link (optional).

2. Question generation
	- Generate short-answer questions only (MVP).
	- Uses a question bank per concept.
	- Uses an evaluator model to reject low-quality generated questions.

3. User interaction
	- Mixed sessions across concepts.
	- Simple responsive UI (mobile + desktop).

4. Feedback mechanism
	- LLM-based grading.
	- If score < 50%: provide a hint.
	- If score is 50–90%: provide model answer + improvement pointers.
	- If score ≥ 90%: keep feedback brief.
	- No retry flow in MVP.

5. Progress tracking + adaptation
	- Track `mastery_streak`, `last_correct_at`, and `next_due_at` per concept.
	- Bias next questions toward concepts sharing tags/topics with the last N questions (N = 3).
	- Hard cooldown scheduling with a 10-minute minimum cooldown after a poor result.

6. Reporting poor questions
	- Users can report a question as poor.
	- Evaluator re-checks the question and removes/replaces it if confirmed poor.


## Technology stack

- Frontend: React
- Backend: FastAPI
- Persistence (MVP): YAML files in `data/` behind a storage abstraction
- AI: Ollama models for generation/grading + a separate evaluator pass (model TBD; placeholder Qwen 10–20B)


## Architecture decisions (living section)

### ADR-001: Storage
- Decision: start with YAML files in `data/` with an abstraction layer so we can later migrate to PostgreSQL.
- Rationale: fastest MVP iteration while preserving a clean migration path.

### ADR-002: AI dependency
- Decision: Ollama is required for practice (block practice if AI is down).
- Rationale: keeps behavior consistent; avoids degraded or misleading practice sessions.

### ADR-003: Question quality gate
- Decision: every newly generated question is validated by an evaluator model; discard and regenerate if it fails evaluation.
- Rationale: keeps the question bank clean and reduces user frustration.

### ADR-004: Mastery-based cooldown scheduling
- Decision: schedule concepts using `mastery_streak` and time-based cooldowns (minutes).
- Rationale: simple spaced repetition behavior without explicitly modeling difficulty.


## Domain rules (MVP)

### Grading thresholds
- Correct: score ≥ 85%
- Poor: score < 50%
- Partial: 50–85%

Notes:
- “Correct” (≥85%) updates `last_correct_at`.
- “Partial” uses model answer feedback; “Poor” uses model answer feedback.


### Mastery and cooldown

Per concept, we maintain:
- `mastery_streak` (integer ≥ 0)
- `last_correct_at` (timestamp)
- `next_due_at` (timestamp)

Mastery updates after each answer submission:
- If score ≥ 85%: `mastery_streak += 1`
- If score is 50–85% and `mastery_streak >= 3`: `mastery_streak = max(0, mastery_streak - 1)`
- If score is 0–50% and `mastery_streak >= 3`: `mastery_streak = max(0, mastery_streak - 3)`
- If `mastery_streak < 3` and score < 85%: `mastery_streak = 0`

Cooldown computation (after updating mastery):

- Base cooldown after a correct (≥85%) answer: 1440 minutes.
- Multipliers:
	- mastery streak levels 1–5: multiply by 1.3 per increment
	- mastery streak levels 6+: multiply by 3.0 per increment

Formula:
- `cooldown_minutes = 1440 * (1.3 ** min(mastery_streak - 1, 4)) * (3.0 ** max(mastery_streak - 5, 0))`

Hard cooldown:
- A concept is due if `now >= next_due_at` (or `next_due_at` is missing).
- No “exception probability” for selecting cooled-down concepts in MVP (0%).

Poor-answer minimum cooldown:
- If score < 50%, set `next_due_at = now + 10 minutes`.


### Mixed session selection (concept choice)

Selection happens in two stages:
1) pick a due concept (weighted)
2) pick or generate a question for that concept

Proposed weights (tunable; may be adjusted later based on testing):
- Start `weight = 1.0` for each due concept.
- Tag/topic continuity (last N questions, N = 3):
	- `tag_overlap = |concept.tags ∩ recent_tags|`
	- `weight *= (1 + tag_overlap * 0.5)`
- Recency (prefer not-correct-recently):
	- If `last_correct_at` is missing: `weight *= 1.5`
	- Else: `weight *= clamp(1.0, 2.0, minutes_since_last_correct / 1440)`
- Poor-answer boost:
	- If last attempt for this concept was poor (<50%): `weight *= 2.0`
- Mastery penalty:
	- `weight *= 1 / (1 + mastery_streak * 0.25)`


## Question bank + evaluator

### Bank rules
- Bank scope: per concept.
- Bank cap: 10 questions per concept.

Generate vs draw:
- If bank size is 0: generate.
- If bank is at cap (10): always draw.
- Otherwise:
	- generate with probability `p_new`
	- else draw uniformly at random from the bank

`p_new` decay:
- Start `p_new = 0.50`.
- Each time a new question is created + saved for that concept: `p_new *= 0.8`.
- When bank reaches cap: `p_new = 0`.

Possible future improvement:
- avoid repeating the same question in the last 3 questions if alternatives exist.


### Evaluator model requirements
For each newly generated question, evaluator must return a strict decision (pass/fail) based on:
- relevance to concept/tags
- clarity and unambiguous wording
- not extreme difficulty (we don’t model difficulty levels, but we should avoid unusable items)
- presence of a plausible model answer / grading rubric

If evaluation fails:
- discard and regenerate (with a capped retry count)


### User reporting poor questions
- User can report a question as poor.
- Evaluator re-checks the question.
	- If confirmed poor: remove from bank and generate a replacement (also evaluated before saving).
	- If not confirmed: keep question; store the report event for later review.


## API surfaces (summary)

HTTP endpoints (to be documented under `API_specifications/`):
- `POST /concepts`
- `GET /concepts`
- `GET /concepts/{id}`
- `POST /practice/generate`
- `POST /practice/submit`
- `POST /questions/{id}/report` (report poor question)
- `GET /progress` (and/or `GET /concepts/{id}/progress`)


## Step-by-step implementation plan (updated)

### Phase 1 — Scaffolding + local dev
1. Create repo structure (`backend/`, `frontend/`, `data/`).
2. Add minimal FastAPI app with `/health`.
3. Add minimal React app that can call `/health`.
4. Add `.env` plumbing for backend (Ollama URL, model names, data dir).

Acceptance check:
- Backend and frontend run locally; `/health` works.


### Phase 2 — Storage + domain model (YAML)
1. Define YAML storage schemas for:
	- concepts
	- progress (mastery, due timestamps)
	- attempts
	- question bank
	- question reports
2. Implement a storage abstraction (atomic writes, validation).

Acceptance check:
- Data persists across restarts; no file corruption on partial writes.


### Phase 3 — Core domain engine
1. Implement mastery update rules.
2. Implement cooldown computation.
3. Implement concept selection with weights and tag continuity.
4. Implement question bank rules (`p_new` decay, cap, uniform draw).

Acceptance check:
- Given mocked attempts, engine produces expected `next_due_at` and concept selection probabilities.


### Phase 4 — Ollama integration (generation, grading, evaluation)
1. Implement Ollama client.
2. Implement generation prompt and strict JSON output.
3. Implement grading prompt and strict JSON output.
4. Implement evaluator prompt and strict JSON output.
5. Block practice endpoints when AI is down.

Acceptance check:
- Generation → evaluation → save-to-bank loop works; failures regenerate.


### Phase 5 — Backend HTTP API
1. Implement concept endpoints.
2. Implement practice generate/submit endpoints.
3. Implement report-poor endpoint.
4. Document each endpoint in `API_specifications/`.

Acceptance check:
- End-to-end flow works via HTTP client and data persists.


### Phase 6 — Frontend MVP
1. Concept list + create.
2. Practice view (question, answer input, feedback).
3. Progress view.
4. Report poor question button.

Acceptance check:
- A user can complete the full loop from the browser.


### Phase 7 — Tests + reliability
1. Unit tests for mastery/cooldown and selection.
2. Storage tests for atomic writes.
3. Mocked tests for evaluator gating.

Acceptance check:
- Core logic is covered by deterministic tests.


## Future features

- Tasks/exercises (with structured submissions)
- User-selected focus topics/tags for a practice session
- Multi-user accounts
- Avoid-repeat logic for question bank draws
	- Basic content filtering if needed for safety and quality

	- Ensure the evaluator output is also strict JSON to drive pass/fail decisions



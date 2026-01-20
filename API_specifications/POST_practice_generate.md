# POST /practice/generate

## Purpose
- Generate a single short-answer practice question.
- Selects a due concept using weighted selection.
- Uses a per-concept question bank (draw or generate).
- Blocks if no concepts are due.
- Blocks if AI (Ollama) is unavailable.

## Auth
- MVP: none (single-user local).

## Request
### Headers
- `Content-Type: application/json`

### Body schema
- No request body.

### Example
```json
{}
```

## Response
### Success
- Status: `200`

#### Body schema
```json
{
  "concept_id": "string",
  "question": {
    "id": "string",
    "concept_id": "string",
    "question_text": "string",
    "model_answer": "string",
    "rubric": "string",
    "created_at": "2026-01-20T12:00:00Z",
    "updated_at": "2026-01-20T12:00:00Z"
  }
}
```

### Errors
- `409` No concepts due
- `503` AI unavailable

#### Example error bodies
```json
{
  "detail": {
    "error": {
      "code": "no_concepts_due",
      "message": "No concepts are due"
    }
  }
}
```

```json
{
  "detail": {
    "error": {
      "code": "ai_unavailable",
      "message": "..."
    }
  }
}
```

## Notes
- Tag continuity is derived from the last 3 attempts by unioning their concept tags.
- Question generation is evaluated; the server may regenerate up to a capped number of times.

# GET /concepts/{id}/progress

## Purpose
- Fetch progress for a single concept.

## Auth
- MVP: none (single-user local).

## Request
### Headers
- None

### Path params
- `id` (string): Concept id.

## Response
### Success
- Status: `200`

#### Body schema
```json
{
  "concept_id": "string",
  "progress": {
    "concept_id": "string",
    "mastery_streak": 0,
    "last_correct_at": "2026-01-20T12:00:00Z",
    "next_due_at": "2026-01-21T12:00:00Z",
    "last_attempt_score": 0
  },
  "is_due": true
}
```

### Errors
- `404` Concept not found

#### Example error body
```json
{
  "detail": {
    "error": {
      "code": "concept_not_found",
      "message": "Concept not found"
    }
  }
}
```

## Notes
- If the concept exists but has no stored progress yet, default progress values are returned.

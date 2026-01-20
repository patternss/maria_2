# GET /progress

## Purpose
- List per-concept progress for all concepts.
- Includes whether each concept is currently due.

## Auth
- MVP: none (single-user local).

## Request
### Headers
- None

### Body
- None

## Response
### Success
- Status: `200`

#### Body schema
```json
{
  "items": [
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
  ]
}
```

### Errors
- None specific (empty list when no concepts exist).

## Notes
- If a concept has no stored progress yet, default progress values are returned.

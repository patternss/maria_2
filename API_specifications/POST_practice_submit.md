# POST /practice/submit

## Purpose
- Submit a user answer for grading.
- Persists an attempt record.
- Updates per-concept progress (`mastery_streak`, `last_correct_at`, `next_due_at`, `last_attempt_score`).

## Auth
- MVP: none (single-user local).

## Request
### Headers
- `Content-Type: application/json`

### Body schema
```json
{
  "concept_id": "string",
  "question_id": "string",
  "user_answer": "string (min length 1)"
}
```

### Example
```json
{
  "concept_id": "...",
  "question_id": "...",
  "user_answer": "My answer..."
}
```

## Response
### Success
- Status: `200`

#### Body schema
```json
{
  "attempt": {
    "id": "string",
    "concept_id": "string",
    "question_id": "string",
    "user_answer": "string",
    "score": 0,
    "feedback": "string",
    "created_at": "2026-01-20T12:00:00Z"
  },
  "progress": {
    "concept_id": "string",
    "mastery_streak": 0,
    "last_correct_at": "2026-01-20T12:00:00Z",
    "next_due_at": "2026-01-21T12:00:00Z",
    "last_attempt_score": 0
  }
}
```

### Errors
- `404` Not found (unknown concept or question)
- `503` AI unavailable

#### Example error body
```json
{
  "detail": {
    "error": {
      "code": "not_found",
      "message": "Question not found"
    }
  }
}
```

## Notes
- Correct threshold for progress updates: score ≥ 85%.
- Poor threshold: score < 50% (triggers minimum 10-minute cooldown).
- OK scores (50–85%) do not update `next_due_at`.

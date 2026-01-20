# POST /questions/{id}/report

## Purpose
- Report a question as potentially poor.
- Always stores the report event.
- Re-evaluates the question with the evaluator model.
- If evaluator confirms poor (pass=false), the question is removed from the bank.

## Auth
- MVP: none (single-user local).

## Request
### Headers
- `Content-Type: application/json`

### Body schema
```json
{
  "reason": "string | null"
}
```

### Example
```json
{
  "reason": "Ambiguous wording"
}
```

## Response
### Success
- Status: `200`

#### Body schema
```json
{
  "removed": true
}
```

### Errors
- `404` Question not found (or concept missing for the stored question)
- `503` AI unavailable

#### Example error body
```json
{
  "detail": {
    "error": {
      "code": "question_not_found",
      "message": "Question not found"
    }
  }
}
```

## Notes
- Confirmed-poor questions are removed.
- The server attempts to generate and evaluator-validate a replacement for the same concept (best-effort).

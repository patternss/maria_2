# GET /concepts

## Purpose
- List all stored concepts.

## Auth
- None (MVP single-user).

## Request
### Headers
- `Content-Type: application/json`

### Body
- None.

## Response
### Success
- Status: `200`

#### Body schema
- Array of `Concept` objects.

#### Example
```json
[
  {
    "id": "9d3a5d8d-0fbe-4a87-9a88-4d4b6a55d3e1",
    "title": "Bayes theorem",
    "description": "Optional",
    "tags": ["probability"],
    "source_url": "https://example.com",
    "created_at": "2026-01-20T12:00:00Z",
    "updated_at": "2026-01-20T12:00:00Z"
  }
]
```

### Errors
- `500` Internal error (unexpected)

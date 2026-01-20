# POST /concepts

## Purpose
- Create a new concept.

## Auth
- None (MVP single-user).

## Request
### Headers
- `Content-Type: application/json`

### Body schema
- `title`: string (required)
- `description`: string | null (optional)
- `tags`: string[] (optional)
- `source_url`: string | null (optional)

### Example
```json
{
  "title": "Bayes theorem",
  "description": "Updating beliefs with evidence.",
  "tags": ["probability", "statistics"],
  "source_url": "https://en.wikipedia.org/wiki/Bayes%27_theorem"
}
```

## Response
### Success
- Status: `201`

#### Example
```json
{
  "id": "9d3a5d8d-0fbe-4a87-9a88-4d4b6a55d3e1",
  "title": "Bayes theorem",
  "description": "Updating beliefs with evidence.",
  "tags": ["probability", "statistics"],
  "source_url": "https://en.wikipedia.org/wiki/Bayes%27_theorem",
  "created_at": "2026-01-20T12:00:00Z",
  "updated_at": "2026-01-20T12:00:00Z"
}
```

### Errors
- `400` Validation error

# GET /concepts/{concept_id}

## Purpose
- Retrieve a single concept by ID.

## Auth
- None (MVP single-user).

## Request
### Path params
- `concept_id`: UUID string

## Response
### Success
- Status: `200`

#### Example
```json
{
  "id": "9d3a5d8d-0fbe-4a87-9a88-4d4b6a55d3e1",
  "title": "Bayes theorem",
  "description": "Updating beliefs with evidence.",
  "tags": ["probability"],
  "source_url": null,
  "created_at": "2026-01-20T12:00:00Z",
  "updated_at": "2026-01-20T12:00:00Z"
}
```

### Errors
- `404` Not found

Example:
```json
{
  "error": {
    "code": "concept_not_found",
    "message": "Concept not found"
  }
}
```

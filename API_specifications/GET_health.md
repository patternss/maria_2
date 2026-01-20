# GET /health

## Purpose
- Simple health check for the backend process.

## Auth
- None (MVP).

## Request
### Headers
- `Content-Type: application/json`

### Body
- None.

## Response
### Success
- Status: `200`

#### Example
```json
{ "status": "ok" }
```

### Errors
- None expected.

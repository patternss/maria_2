from __future__ import annotations

import sys
import asyncio
from pprint import pprint
from uuid import uuid4

import httpx


def _fail(message: str) -> None:
    raise SystemExit(message)


def _print_response(label: str, resp: httpx.Response) -> None:
    print(f"\n== {label} ==")
    print(f"{resp.status_code}")
    try:
        pprint(resp.json())
    except Exception:  # noqa: BLE001
        print(resp.text)


async def main() -> None:
    # Ensure `import app.*` works when running from repo root.
    sys.path.insert(0, "/Users/home/omat/maria_2/backend")

    from app.main import create_app  # local import to respect sys.path above

    app = create_app()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        _print_response("GET /health", r)
        if r.status_code != 200:
            _fail("Health check failed")

        r = await client.get("/concepts")
        _print_response("GET /concepts", r)
        if r.status_code != 200:
            _fail("List concepts failed")

        unique = str(uuid4())[:8]
        r = await client.post(
            "/concepts",
            json={
                "title": f"Smoke test concept {unique}",
                "description": "Created by backend/scripts/smoke_test.py",
                "tags": ["smoke", "test"],
                "source_url": "https://example.com",
            },
        )
        _print_response("POST /concepts", r)
        if r.status_code != 201:
            _fail("Create concept failed")

        concept = r.json()
        concept_id = concept["id"]

        r = await client.get(f"/concepts/{concept_id}")
        _print_response("GET /concepts/{id}", r)
        if r.status_code != 200:
            _fail("Get concept failed")

        r = await client.get("/progress")
        _print_response("GET /progress", r)
        if r.status_code != 200:
            _fail("List progress failed")

        r = await client.get(f"/concepts/{concept_id}/progress")
        _print_response("GET /concepts/{id}/progress", r)
        if r.status_code != 200:
            _fail("Get concept progress failed")

        # AI-gated endpoints: OK if 503 when Ollama is down.
        r = await client.post("/practice/generate")
        _print_response("POST /practice/generate (AI-gated)", r)
        if r.status_code not in (200, 503, 409):
            _fail("Unexpected status for /practice/generate")

        # With a fake id, this should be 404 (or 503 if AI is down before lookup).
        r = await client.post("/questions/not-a-real-question-id/report", json={"reason": "smoke test"})
        _print_response("POST /questions/{id}/report (fake id)", r)
        if r.status_code not in (404, 503):
            _fail("Unexpected status for /questions/{id}/report")

        print("\nSMOKE TEST: OK")


if __name__ == "__main__":
    asyncio.run(main())

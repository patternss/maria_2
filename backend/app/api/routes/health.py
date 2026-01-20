from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint.

    Purpose:
        Allows local dev and monitoring tools to verify the API process is up.

    Inputs:
        None.

    Outputs:
        JSON object with a simple status string.

    Error cases:
        None expected.
    """

    return {"status": "ok"}

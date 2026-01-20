from __future__ import annotations

import json
from dataclasses import dataclass

import httpx


class OllamaUnavailable(RuntimeError):
    """Raised when Ollama cannot be reached or returns an error."""


@dataclass(frozen=True)
class OllamaModelConfig:
    base_url: str
    model: str


class OllamaClient:
    """Minimal Ollama HTTP client.

    Purpose:
        Provide a single place for calling Ollama and handling timeouts/errors.

    Notes:
        We use the Ollama `/api/generate` endpoint with JSON schema instructions.
    """

    def __init__(self, *, base_url: str, timeout_seconds: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    def generate_json(self, *, model: str, prompt: str) -> dict:
        """Generate a JSON object from the model.

        Inputs:
            model: Ollama model name.
            prompt: Prompt text.

        Outputs:
            Parsed JSON object.

        Raises:
            OllamaUnavailable: if Ollama is unreachable or returns non-JSON.
        """

        url = f"{self._base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=payload)
        except Exception as exc:  # noqa: BLE001
            raise OllamaUnavailable(str(exc)) from exc

        if response.status_code >= 400:
            raise OllamaUnavailable(f"Ollama error {response.status_code}: {response.text}")

        data = response.json()
        text = data.get("response", "")

        try:
            return json.loads(text)
        except Exception as exc:  # noqa: BLE001
            raise OllamaUnavailable(f"Model returned non-JSON: {text[:200]}") from exc

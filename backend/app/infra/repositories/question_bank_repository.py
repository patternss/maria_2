from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.domain.practice.models import PracticeQuestion
from app.infra.storage.yaml_store import YamlStore


class QuestionBankRepository:
    """Repository for per-concept question banks.

    Storage:
        YAML file `question_bank.yaml`.

    Schema:
        {
          version: 1,
          banks: [
            {
              concept_id: str,
              p_new: float,
              questions: [PracticeQuestion, ...]
            }
          ]
        }
    """

    _FILENAME = "question_bank.yaml"
    _CAP = 10

    def __init__(self, store: YamlStore) -> None:
        self._store = store

    def _read_payload(self) -> dict:
        return self._store.read(self._FILENAME, default={"version": 1, "banks": []})

    def _write_payload(self, payload: dict) -> None:
        self._store.write_atomic(self._FILENAME, payload)

    def get_bank(self, concept_id: str) -> tuple[float, list[PracticeQuestion]]:
        payload = self._read_payload()
        for bank in payload.get("banks", []):
            if bank.get("concept_id") == concept_id:
                p_new = float(bank.get("p_new", 0.5))
                questions = [PracticeQuestion.model_validate(q) for q in bank.get("questions", [])]
                return p_new, questions
        return 0.5, []

    def save_bank(self, concept_id: str, *, p_new: float, questions: list[PracticeQuestion]) -> None:
        payload = self._read_payload()
        payload.setdefault("version", 1)
        payload.setdefault("banks", [])

        banks: list[dict] = []
        replaced = False
        for bank in payload["banks"]:
            if bank.get("concept_id") == concept_id:
                banks.append(
                    {
                        "concept_id": concept_id,
                        "p_new": p_new,
                        "questions": [q.model_dump(mode="json") for q in questions],
                    }
                )
                replaced = True
            else:
                banks.append(bank)

        if not replaced:
            banks.append(
                {
                    "concept_id": concept_id,
                    "p_new": p_new,
                    "questions": [q.model_dump(mode="json") for q in questions],
                }
            )

        payload["banks"] = banks
        self._write_payload(payload)

    def get_question(self, question_id: str) -> PracticeQuestion | None:
        payload = self._read_payload()
        for bank in payload.get("banks", []):
            for q in bank.get("questions", []):
                if q.get("id") == question_id:
                    return PracticeQuestion.model_validate(q)
        return None

    def upsert_question(
        self,
        *,
        concept_id: str,
        question_text: str,
        model_answer: str,
        rubric: str,
        now: datetime | None = None,
    ) -> PracticeQuestion:
        now = now or datetime.now(timezone.utc)

        p_new, questions = self.get_bank(concept_id)

        if len(questions) >= self._CAP:
            raise ValueError("Question bank is full")

        q = PracticeQuestion(
            id=str(uuid4()),
            concept_id=concept_id,
            question_text=question_text,
            model_answer=model_answer,
            rubric=rubric,
            created_at=now,
            updated_at=now,
        )

        questions.append(q)

        # Decay p_new on save of a new question.
        p_new = p_new * 0.8

        self.save_bank(concept_id, p_new=p_new, questions=questions)
        return q

    def remove_question(self, question_id: str) -> bool:
        payload = self._read_payload()
        changed = False

        for bank in payload.get("banks", []):
            before = len(bank.get("questions", []))
            bank["questions"] = [q for q in bank.get("questions", []) if q.get("id") != question_id]
            after = len(bank.get("questions", []))
            if after != before:
                changed = True

        if changed:
            self._write_payload(payload)

        return changed

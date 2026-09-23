from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re
import uuid

from .knowledge import ALIASES, GENERIC_QUESTIONS, OBJECT_KNOWLEDGE, ScienceHint


TOKEN_SPLIT_PATTERN = re.compile(r"[\s_\-.,]+")


@dataclass
class DetectionItem:
    name: str
    confidence: float
    phenomena: list[str]
    suggestedQuestions: list[str]


@dataclass
class RecognitionResult:
    requestId: str
    detections: list[DetectionItem]
    suggestedQuestions: list[str]
    retakeAllowed: bool
    correctionAllowed: bool


class RecognitionService:
    def __init__(self, feedback_file: Path) -> None:
        self.feedback_file = feedback_file
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)

    def recognize(self, file_name: str, user_hint: str | None = None) -> RecognitionResult:
        matched = self._match_objects(file_name, user_hint)
        detections: list[DetectionItem] = []

        if not matched:
            detections.append(
                DetectionItem(
                    name="미확인 대상",
                    confidence=0.25,
                    phenomena=["관찰 필요", "비교 관찰", "시간 변화"],
                    suggestedQuestions=GENERIC_QUESTIONS,
                )
            )
        else:
            for idx, name in enumerate(matched):
                hint = OBJECT_KNOWLEDGE.get(name)
                confidence = max(0.99 - (idx * 0.07), 0.6)
                detections.append(self._to_detection(name, confidence, hint))

        merged_questions = self._merge_questions(detections)
        return RecognitionResult(
            requestId=str(uuid.uuid4()),
            detections=detections,
            suggestedQuestions=merged_questions,
            retakeAllowed=True,
            correctionAllowed=True,
        )

    def save_correction(
        self,
        request_id: str,
        original_name: str,
        corrected_name: str,
        note: str | None = None,
    ) -> None:
        payload = {
            "requestId": request_id,
            "originalName": original_name,
            "correctedName": corrected_name,
            "note": note or "",
        }
        with self.feedback_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _to_detection(
        self,
        name: str,
        confidence: float,
        hint: ScienceHint | None,
    ) -> DetectionItem:
        if hint is None:
            return DetectionItem(
                name=name,
                confidence=confidence,
                phenomena=["관찰 필요", "비교 관찰"],
                suggestedQuestions=GENERIC_QUESTIONS,
            )
        return DetectionItem(
            name=name,
            confidence=round(confidence, 2),
            phenomena=hint.phenomena,
            suggestedQuestions=hint.questions,
        )

    def _match_objects(self, file_name: str, user_hint: str | None) -> list[str]:
        text = f"{file_name} {user_hint or ''}".lower()
        tokens = [token for token in TOKEN_SPLIT_PATTERN.split(text) if token]

        matched: list[str] = []

        for raw_key in OBJECT_KNOWLEDGE.keys():
            if raw_key in text:
                matched.append(raw_key)

        for token in tokens:
            alias_target = ALIASES.get(token)
            if alias_target:
                matched.append(alias_target)

        deduped: list[str] = []
        for name in matched:
            if name not in deduped:
                deduped.append(name)

        return deduped[:5]

    def _merge_questions(self, detections: list[DetectionItem]) -> list[str]:
        merged: list[str] = []
        for detection in detections:
            for q in detection.suggestedQuestions:
                if q not in merged:
                    merged.append(q)
        if not merged:
            return GENERIC_QUESTIONS
        return merged[:6]


def as_api_dict(result: RecognitionResult) -> dict:
    return {
        "requestId": result.requestId,
        "detections": [asdict(d) for d in result.detections],
        "suggestedQuestions": result.suggestedQuestions,
        "retakeAllowed": result.retakeAllowed,
        "correctionAllowed": result.correctionAllowed,
    }

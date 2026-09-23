from __future__ import annotations

from typing import Any


AVAILABLE_LEVELS = ["very_easy", "easy", "detailed", "professional"]


def normalize_question_response(
    response: Any,
    source: str,
    question: str,
    level: str,
) -> dict[str, Any]:
    """외부 API의 여러 응답 형태를 앱의 질문 결과 형식으로 변환합니다."""
    payload = _mapping(response)
    result = _mapping(payload.get("result")) or payload
    answer = _answer_text(result)
    explanation = _explanation(result=result, answer=answer, level=level)

    return {
        "source": source,
        "normalizedQuestion": str(result.get("normalizedQuestion") or question),
        "interpretedTopic": str(result.get("interpretedTopic") or result.get("topic") or "일반"),
        "confidence": _confidence(result.get("confidence")),
        "answerPreview": str(result.get("answerPreview") or answer),
        "suggestedQuestions": _string_list(result.get("suggestedQuestions")),
        "explanation": explanation,
        "observationPlan": _mapping(result.get("observationPlan")),
        "experimentSuggestions": _list_of_mappings(result.get("experimentSuggestions")),
        "relatedQuestions": _string_list(result.get("relatedQuestions")),
        "vaultEntryId": result.get("vaultEntryId"),
    }


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _answer_text(result: dict[str, Any]) -> str:
    for key in ("answerPreview", "answer", "output_text", "text", "content", "message"):
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    output = result.get("output")
    if isinstance(output, list):
        text_parts: list[str] = []
        for item in output:
            for content in _mapping(item).get("content", []):
                content_map = _mapping(content)
                text = content_map.get("text")
                if isinstance(text, str) and text.strip():
                    text_parts.append(text.strip())
        if text_parts:
            return "\n".join(text_parts)

    choices = result.get("choices")
    if isinstance(choices, list) and choices:
        first = _mapping(choices[0])
        message = _mapping(first.get("message"))
        content = message.get("content") or first.get("text")
        if isinstance(content, str) and content.strip():
            return content.strip()

    explanation = result.get("explanation")
    if isinstance(explanation, str) and explanation.strip():
        return explanation.strip()
    if isinstance(explanation, dict) and isinstance(explanation.get("explanation"), str):
        return explanation["explanation"].strip()

    return "외부 API에서 답변을 받았습니다."


def _explanation(result: dict[str, Any], answer: str, level: str) -> dict[str, Any]:
    existing = _mapping(result.get("explanation"))
    return {
        "topic": str(existing.get("topic") or result.get("topic") or result.get("interpretedTopic") or "일반"),
        "selectedLevel": str(existing.get("selectedLevel") or level),
        "explanation": str(existing.get("explanation") or answer),
        "availableLevels": _string_list(existing.get("availableLevels")) or AVAILABLE_LEVELS[:],
        "termHelp": existing.get("termHelp") if isinstance(existing.get("termHelp"), list) else [],
    }


def _confidence(value: Any) -> float:
    try:
        return round(max(0.0, min(1.0, float(value))), 2)
    except (TypeError, ValueError):
        return 0.0


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float))]


def _list_of_mappings(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]

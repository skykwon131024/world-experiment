from __future__ import annotations

from dataclasses import asdict, dataclass

from .knowledge import EXPLANATION_BY_LEVEL, TERM_DEFINITIONS


LEVELS = ("very_easy", "easy", "detailed", "professional")
DEFAULT_LEVEL = "easy"


@dataclass
class TermHelp:
    term: str
    definition: str


@dataclass
class ExplanationResult:
    topic: str
    selectedLevel: str
    explanation: str
    availableLevels: list[str]
    termHelp: list[TermHelp]


class ExplanationService:
    def normalize_level(self, level: str) -> str:
        return self._normalize_level(level)

    def explain(self, topic: str, level: str = DEFAULT_LEVEL) -> ExplanationResult:
        normalized_level = self._normalize_level(level)
        level_map = EXPLANATION_BY_LEVEL.get(topic) or EXPLANATION_BY_LEVEL["일반"]
        explanation = level_map.get(normalized_level) or level_map[DEFAULT_LEVEL]

        found_terms = self._extract_terms(explanation)
        helps = [TermHelp(term=t, definition=TERM_DEFINITIONS[t]) for t in found_terms]

        return ExplanationResult(
            topic=topic,
            selectedLevel=normalized_level,
            explanation=explanation,
            availableLevels=list(LEVELS),
            termHelp=helps,
        )

    def _normalize_level(self, level: str) -> str:
        alias_map = {
            "아주 쉽게": "very_easy",
            "쉽게": "easy",
            "자세히": "detailed",
            "전문적으로": "professional",
            "very_easy": "very_easy",
            "easy": "easy",
            "detailed": "detailed",
            "professional": "professional",
        }
        return alias_map.get(level.strip(), DEFAULT_LEVEL)

    def _extract_terms(self, explanation: str) -> list[str]:
        found: list[str] = []
        for term in TERM_DEFINITIONS.keys():
            if term in explanation and term not in found:
                found.append(term)
        return found


def as_dict(result: ExplanationResult) -> dict:
    return {
        "topic": result.topic,
        "selectedLevel": result.selectedLevel,
        "explanation": result.explanation,
        "availableLevels": result.availableLevels,
        "termHelp": [asdict(item) for item in result.termHelp],
    }

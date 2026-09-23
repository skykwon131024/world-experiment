from __future__ import annotations

from dataclasses import asdict, dataclass

from .knowledge import RELATED_QUESTION_GRAPH


@dataclass
class RelatedQuestionSet:
    topic: str
    currentQuestion: str
    relatedQuestions: list[str]


class RelatedQuestionService:
    def recommend(self, topic: str, current_question: str, limit: int = 4) -> RelatedQuestionSet:
        pool = RELATED_QUESTION_GRAPH.get(topic) or RELATED_QUESTION_GRAPH["일반"]

        filtered = [q for q in pool if q.strip() and q != current_question]
        if not filtered:
            filtered = RELATED_QUESTION_GRAPH["일반"][:]

        return RelatedQuestionSet(
            topic=topic if topic in RELATED_QUESTION_GRAPH else "일반",
            currentQuestion=current_question,
            relatedQuestions=filtered[:limit],
        )


def as_dict(result: RelatedQuestionSet) -> dict:
    return asdict(result)

from __future__ import annotations

from dataclasses import asdict, dataclass

from .vault import CuriosityEntry

DEFAULT_ACTIONS = ["알아보기", "직접 확인하기"]

CATEGORY_QUESTION_BANK: dict[str, list[str]] = {
    "자연": [
        "왜 비가 온 뒤에는 특유의 냄새가 날까요?",
        "왜 해가 질 때 하늘 색이 달라질까요?",
        "바람이 강한 날에는 왜 구름 모양이 빨리 바뀔까요?",
    ],
    "생활": [
        "왜 뜨거운 물컵 주변에는 김이 생길까요?",
        "같은 물도 컵 재질에 따라 왜 빨리 식을까요?",
        "왜 거울은 빛이 없으면 잘 보이지 않을까요?",
    ],
    "동물": [
        "고양이 눈은 밤에 왜 더 밝게 보일까요?",
        "강아지는 왜 냄새를 더 잘 맡을까요?",
        "새들은 왜 무리 지어 움직일까요?",
    ],
    "우주": [
        "왜 달은 위치가 바뀌어도 나를 따라오는 것처럼 보일까요?",
        "왜 별은 반짝이지만 행성은 덜 반짝일까요?",
        "왜 낮에는 별이 잘 보이지 않을까요?",
    ],
    "과학": [
        "왜 얼음은 물에 뜰까요?",
        "왜 같은 양의 물도 놓인 곳에 따라 더 빨리 증발할까요?",
        "왜 금속 숟가락은 플라스틱 숟가락보다 더 차갑게 느껴질까요?",
    ],
    "생명": [
        "식물 잎은 왜 햇빛 쪽으로 기울까요?",
        "왜 씨앗은 물을 만나면 싹이 트기 시작할까요?",
        "왜 사람마다 숨이 찰 때 회복 속도가 다를까요?",
    ],
    "기술": [
        "전자레인지는 왜 음식 위치마다 온도가 다르게 올라갈까요?",
        "왜 휴대폰은 오래 쓰면 따뜻해질까요?",
        "왜 배터리는 추운 날 더 빨리 닳을까요?",
    ],
}

TOPIC_TO_CATEGORY: dict[str, str] = {
    "구름": "자연",
    "물": "자연",
    "얼음": "과학",
    "거울": "생활",
    "전자레인지": "기술",
    "고양이": "동물",
    "나무": "생명",
}


@dataclass
class TodayCuriosity:
    question: str
    category: str
    basedOnHistory: bool
    reason: str
    availableActions: list[str]


class TodayCuriosityService:
    def recommend(self, entries: list[CuriosityEntry], limit: int = 1) -> list[TodayCuriosity]:
        category = self._choose_interest_category(entries)
        based = len(entries) > 0

        bank = CATEGORY_QUESTION_BANK.get(category, CATEGORY_QUESTION_BANK["과학"])
        picks = bank[: max(1, min(limit, len(bank)))]

        reason = self._build_reason(category=category, based_on_history=based)
        return [
            TodayCuriosity(
                question=question,
                category=category,
                basedOnHistory=based,
                reason=reason,
                availableActions=DEFAULT_ACTIONS[:],
            )
            for question in picks
        ]

    def _choose_interest_category(self, entries: list[CuriosityEntry]) -> str:
        if not entries:
            return "자연"

        score: dict[str, int] = {}
        for entry in entries:
            score[entry.category] = score.get(entry.category, 0) + 2
            mapped = TOPIC_TO_CATEGORY.get(entry.topic)
            if mapped:
                score[mapped] = score.get(mapped, 0) + 1

        if not score:
            return "자연"

        best_category = "자연"
        best_score = -1
        for category, point in score.items():
            if point > best_score:
                best_category = category
                best_score = point
        return best_category

    def _build_reason(self, category: str, based_on_history: bool) -> str:
        if based_on_history:
            return f"최근 탐구 기록에서 {category} 분야 관심이 높아 이 질문을 추천했어요."
        return "처음 탐구를 시작하기 좋아서 관찰하기 쉬운 질문을 추천했어요."


def as_dict(item: TodayCuriosity) -> dict:
    return asdict(item)

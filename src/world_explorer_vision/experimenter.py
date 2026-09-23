from __future__ import annotations

from dataclasses import asdict, dataclass

from .knowledge import EXPERIMENT_TEMPLATES


@dataclass
class ExperimentPlan:
    title: str
    purpose: str
    materials: list[str]
    steps: list[str]
    expectedResult: str
    duration: str
    difficulty: str
    safety: list[str]
    reason: str


class ExperimentService:
    def suggest(self, topic: str, available_items: list[str] | None = None, limit: int = 3) -> list[ExperimentPlan]:
        normalized_items = [item.strip() for item in (available_items or []) if item.strip()]
        pool = EXPERIMENT_TEMPLATES.get(topic) or EXPERIMENT_TEMPLATES["일반"]

        matched: list[ExperimentPlan] = []
        fallback: list[ExperimentPlan] = []

        for template in pool:
            required = [str(x) for x in template.get("requiredItems", [])]
            plan = ExperimentPlan(
                title=str(template["title"]),
                purpose=str(template["purpose"]),
                materials=[str(x) for x in template["materials"]],
                steps=[str(x) for x in template["steps"]],
                expectedResult=str(template["expectedResult"]),
                duration=str(template["duration"]),
                difficulty=str(template["difficulty"]),
                safety=[str(x) for x in template["safety"]],
                reason=self._build_reason(topic=topic, required_items=required, available_items=normalized_items),
            )

            if self._is_item_match(required_items=required, available_items=normalized_items):
                matched.append(plan)
            else:
                fallback.append(plan)

        ordered = matched + fallback
        if not ordered:
            ordered = [self._default_plan(topic)]
        return ordered[:limit]

    def _default_plan(self, topic: str) -> ExperimentPlan:
        return ExperimentPlan(
            title="변수 하나 바꾸기 기본 실험",
            purpose=f"{topic}와 관련된 변화를 직접 관찰",
            materials=["관찰 대상", "기록 도구", "타이머"],
            steps=[
                "처음 상태를 기록합니다.",
                "조건 하나를 바꿉니다.",
                "5분 간격으로 변화를 3회 기록합니다.",
            ],
            expectedResult="조건 변화에 따라 결과가 달라질 수 있습니다.",
            duration="10분",
            difficulty="쉬움",
            safety=["안전한 장소에서 진행하세요."],
            reason="기본 실험 템플릿으로 추천되었습니다.",
        )

    def _is_item_match(self, required_items: list[str], available_items: list[str]) -> bool:
        if not required_items:
            return True
        if not available_items:
            return False

        available_set = {item.lower() for item in available_items}
        for need in required_items:
            if need.lower() not in available_set:
                return False
        return True

    def _build_reason(self, topic: str, required_items: list[str], available_items: list[str]) -> str:
        if not required_items:
            return f"{topic} 질문에 맞는 기본 실험입니다."
        if not available_items:
            return f"{topic} 질문과 관련된 대표 실험입니다."

        missing = [item for item in required_items if item.lower() not in {x.lower() for x in available_items}]
        if missing:
            joined = ", ".join(missing)
            return f"현재 가진 물건 기준으로 일부 준비물이 더 필요합니다: {joined}."

        return "입력한 주변 물건으로 바로 진행할 수 있는 실험입니다."


def as_dict(plan: ExperimentPlan) -> dict:
    return asdict(plan)

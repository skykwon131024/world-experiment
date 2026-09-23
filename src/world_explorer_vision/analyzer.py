from __future__ import annotations

from dataclasses import asdict, dataclass
import re

from .experimenter import ExperimentPlan, as_dict as experiment_as_dict
from .recorder import ExperimentRecord


WORD_SPLIT = re.compile(r"[\s,.;:!?]+")


TOPIC_PRINCIPLES: dict[str, str] = {
    "얼음": "주변 온도와 빛으로 전달되는 열의 차이가 녹는 속도 차이를 만들 수 있습니다.",
    "물": "표면장력과 증발 속도 차이가 물방울의 모양과 변화 속도에 영향을 줍니다.",
    "거울": "빛의 반사 방향은 거울 각도에 따라 달라지며, 보이는 위치 변화로 확인할 수 있습니다.",
    "구름": "공기 온도와 수증기 상태가 응결에 영향을 주어 구름 형태 변화를 만듭니다.",
    "전자레인지": "전자기파에 의한 가열은 위치와 구성 성분에 따라 온도 분포가 달라질 수 있습니다.",
    "일반": "조건 변화가 결과 차이를 만들 수 있으므로 한 번에 한 조건만 바꿔 비교하는 것이 좋습니다.",
}


TOPIC_CAUSES: dict[str, list[str]] = {
    "얼음": ["온도 차이", "햇빛 노출", "바람 세기", "접촉 면적"],
    "물": ["표면 재질", "온도", "습도", "물방울 크기"],
    "거울": ["거울 각도", "빛 세기", "빛 방향"],
    "구름": ["바람 방향", "습도 변화", "기온 변화"],
    "전자레인지": ["가열 위치", "가열 시간", "음식 수분량"],
    "일반": ["온도", "시간", "위치", "주변 환경"],
}


@dataclass
class ExperimentAnalysis:
    topic: str
    expectedResult: str
    actualResult: str
    matchStatus: str
    comparisonSummary: str
    likelyCauses: list[str]
    sciencePrinciple: str
    possibleErrors: list[str]
    nextExperiments: list[dict]


class ExperimentAnalysisService:
    def analyze(self, record: ExperimentRecord, topic: str, next_plans: list[ExperimentPlan]) -> ExperimentAnalysis:
        expected = record.expectedResult.strip()
        actual = record.actualResult.strip()

        match_status, summary = self._compare(expected, actual)
        causes = self._build_causes(topic=topic, record=record)
        principle = TOPIC_PRINCIPLES.get(topic, TOPIC_PRINCIPLES["일반"])
        errors = self._possible_errors(record)

        return ExperimentAnalysis(
            topic=topic,
            expectedResult=expected,
            actualResult=actual,
            matchStatus=match_status,
            comparisonSummary=summary,
            likelyCauses=causes,
            sciencePrinciple=principle,
            possibleErrors=errors,
            nextExperiments=[experiment_as_dict(plan) for plan in next_plans[:2]],
        )

    def _compare(self, expected: str, actual: str) -> tuple[str, str]:
        if not expected or not actual:
            return (
                "insufficient",
                "예상 결과 또는 실제 결과가 비어 있어 비교를 완료할 수 없습니다.",
            )

        if self._looks_same(expected, actual):
            return (
                "matched",
                "예상한 방향과 실제 관찰 결과가 전반적으로 일치합니다.",
            )

        return (
            "mismatched",
            "예상과 실제 결과가 달라 추가 원인 확인이 필요합니다.",
        )

    def _looks_same(self, expected: str, actual: str) -> bool:
        if _normalize(expected) == _normalize(actual):
            return True

        tokens_expected = set(_tokens(expected))
        tokens_actual = set(_tokens(actual))
        overlap = tokens_expected.intersection(tokens_actual)
        return len(overlap) >= 2

    def _build_causes(self, topic: str, record: ExperimentRecord) -> list[str]:
        base = TOPIC_CAUSES.get(topic, TOPIC_CAUSES["일반"])
        causes = base[:]

        note_text = " ".join(record.observationNotes)
        if "햇빛" in note_text and "햇빛 노출" not in causes:
            causes.insert(0, "햇빛 노출")
        if "그늘" in note_text and "위치" not in causes:
            causes.append("위치")
        if record.measurements and "측정 시점 차이" not in causes:
            causes.append("측정 시점 차이")

        deduped: list[str] = []
        for item in causes:
            if item not in deduped:
                deduped.append(item)
        return deduped[:4]

    def _possible_errors(self, record: ExperimentRecord) -> list[str]:
        errors: list[str] = []

        if not record.startPhotos:
            errors.append("실험 시작 사진이 없어 초기 상태 비교가 어렵습니다.")
        if not record.endPhotos:
            errors.append("실험 종료 사진이 없어 결과 비교 근거가 약할 수 있습니다.")
        if len(record.measurements) < 2:
            errors.append("측정값이 적어 경향 판단의 신뢰도가 낮을 수 있습니다.")
        if not record.observationNotes:
            errors.append("관찰 메모가 없어 결과 해석 단서가 부족합니다.")

        if not errors:
            errors.append("기록 품질은 양호합니다. 같은 조건으로 한 번 더 반복하면 신뢰도를 높일 수 있습니다.")

        return errors


def _normalize(text: str) -> str:
    return "".join(ch for ch in text.lower() if ch.isalnum())


def _tokens(text: str) -> list[str]:
    return [token for token in WORD_SPLIT.split(text.lower()) if token]


def as_dict(result: ExperimentAnalysis) -> dict:
    return asdict(result)

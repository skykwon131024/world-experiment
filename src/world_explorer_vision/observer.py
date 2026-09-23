from __future__ import annotations

from dataclasses import asdict, dataclass

from .knowledge import OBSERVATION_GUIDES


@dataclass
class ObservationPlan:
    topic: str
    whatToObserve: str
    method: str
    observationTime: str
    checkpoints: list[str]
    expectedChanges: list[str]


class ObservationService:
    def create_plan(self, topic: str) -> ObservationPlan:
        guide = OBSERVATION_GUIDES.get(topic, OBSERVATION_GUIDES["일반"])
        return ObservationPlan(
            topic=topic if topic in OBSERVATION_GUIDES else "일반",
            whatToObserve=str(guide["whatToObserve"]),
            method=str(guide["method"]),
            observationTime=str(guide["observationTime"]),
            checkpoints=list(guide["checkpoints"]),
            expectedChanges=list(guide["expectedChanges"]),
        )


def as_dict(plan: ObservationPlan) -> dict:
    return asdict(plan)

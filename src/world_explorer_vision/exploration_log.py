from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from .catalog import FieldCatalog
from .step_guide import ExperimentGuideState
from .vault import CuriosityEntry


@dataclass
class ExplorationRecord:
    solvedCuriosityCount: int
    completedExperimentCount: int
    observedObjectCount: int
    discoveredPrincipleCount: int
    exploredCategories: list[str]
    consecutiveExplorationDays: int
    summary: list[str]


class ExplorationLogService:
    def build(
        self,
        vault_entries: list[CuriosityEntry],
        experiment_sessions: list[ExperimentGuideState],
        catalogs: list[FieldCatalog],
    ) -> ExplorationRecord:
        solved_curiosity_count = len(vault_entries)

        completed_experiment_count = 0
        for session in experiment_sessions:
            if session.status == "completed":
                completed_experiment_count += 1

        topic_set: set[str] = set()
        explored_categories: list[str] = []
        for entry in vault_entries:
            if entry.topic != "일반":
                topic_set.add(entry.topic)
            if entry.category not in explored_categories:
                explored_categories.append(entry.category)

        discovered_set: set[str] = set()
        for catalog in catalogs:
            for item in catalog.discoveredPrinciples:
                discovered_set.add(item.principle)

        consecutive_days = self._compute_streak(vault_entries)

        return ExplorationRecord(
            solvedCuriosityCount=solved_curiosity_count,
            completedExperimentCount=completed_experiment_count,
            observedObjectCount=len(topic_set),
            discoveredPrincipleCount=len(discovered_set),
            exploredCategories=explored_categories,
            consecutiveExplorationDays=consecutive_days,
            summary=[
                f"궁금증 해결 {solved_curiosity_count}개",
                f"실험 완료 {completed_experiment_count}회",
                f"발견한 원리 {len(discovered_set)}개",
                f"새로운 질문 {solved_curiosity_count}개",
            ],
        )

    def _compute_streak(self, vault_entries: list[CuriosityEntry]) -> int:
        if not vault_entries:
            return 0

        dates: set[datetime] = set()
        for entry in vault_entries:
            dt = self._parse_iso_utc(entry.askedAt)
            dates.add(datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc))

        sorted_dates = sorted(dates)
        streak = 1
        best = 1
        for i in range(1, len(sorted_dates)):
            diff = (sorted_dates[i] - sorted_dates[i - 1]).days
            if diff == 1:
                streak += 1
                if streak > best:
                    best = streak
            elif diff > 1:
                streak = 1

        return best

    def _parse_iso_utc(self, value: str) -> datetime:
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)


def as_dict(record: ExplorationRecord) -> dict:
    return asdict(record)
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import uuid

ALLOWED_CATEGORIES = ["자연", "생활", "동물", "우주", "과학", "생명", "기술"]
DEFAULT_CATEGORY = "과학"


def _utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


@dataclass
class CuriosityEntry:
    entryId: str
    question: str
    aiAnswer: str
    askedAt: str
    relatedPhotos: list[str] = field(default_factory=list)
    relatedExperiment: str | None = None
    discoveredPrinciples: list[str] = field(default_factory=list)
    category: str = DEFAULT_CATEGORY
    topic: str = "일반"
    source: str = "text"


class CuriosityVaultService:
    def __init__(self) -> None:
        self._entries: dict[str, CuriosityEntry] = {}
        self._order: list[str] = []

    def save(
        self,
        question: str,
        ai_answer: str,
        topic: str,
        source: str,
        related_photos: list[str] | None = None,
        related_experiment: str | None = None,
        discovered_principles: list[str] | None = None,
        category: str | None = None,
    ) -> CuriosityEntry:
        resolved_category = self._normalize_category(category or self._classify(question=question, topic=topic))
        entry = CuriosityEntry(
            entryId=str(uuid.uuid4()),
            question=question,
            aiAnswer=ai_answer,
            askedAt=_utc_now_iso(),
            relatedPhotos=related_photos or [],
            relatedExperiment=related_experiment,
            discoveredPrinciples=discovered_principles or [],
            category=resolved_category,
            topic=topic,
            source=source,
        )
        self._entries[entry.entryId] = entry
        self._order.append(entry.entryId)
        return entry

    def list_entries(self, category: str | None = None, keyword: str | None = None) -> list[CuriosityEntry]:
        items = [self._entries[item_id] for item_id in reversed(self._order)]

        if category:
            resolved = self._normalize_category(category)
            items = [item for item in items if item.category == resolved]

        if keyword and keyword.strip():
            token = keyword.strip().lower()
            items = [item for item in items if self._matches_keyword(item, token)]

        return items

    def search(self, keyword: str) -> list[CuriosityEntry]:
        return self.list_entries(keyword=keyword)

    def update_category(self, entry_id: str, new_category: str) -> CuriosityEntry:
        entry = self.get_entry(entry_id)
        entry.category = self._normalize_category(new_category)
        return entry

    def get_entry(self, entry_id: str) -> CuriosityEntry:
        if entry_id not in self._entries:
            raise ValueError("존재하지 않는 보관함 항목입니다.")
        return self._entries[entry_id]

    def attach_experiment_by_topic(self, topic: str, experiment_session_id: str) -> CuriosityEntry | None:
        for item_id in reversed(self._order):
            item = self._entries[item_id]
            if item.topic == topic and not item.relatedExperiment:
                item.relatedExperiment = experiment_session_id
                return item
        return None

    def add_discovered_principle_by_topic(self, topic: str, principle: str) -> CuriosityEntry | None:
        clean = principle.strip()
        if not clean:
            return None

        for item_id in reversed(self._order):
            item = self._entries[item_id]
            if item.topic != topic:
                continue
            if clean not in item.discoveredPrinciples:
                item.discoveredPrinciples.append(clean)
            return item
        return None

    def _classify(self, question: str, topic: str) -> str:
        q = question.lower()
        topic_map = {
            "구름": "자연",
            "물": "자연",
            "얼음": "과학",
            "거울": "생활",
            "전자레인지": "기술",
        }
        if topic in topic_map:
            return topic_map[topic]

        if "동물" in q or "강아지" in q or "고양이" in q:
            return "동물"
        if "우주" in q or "달" in q or "별" in q or "행성" in q:
            return "우주"
        if "식물" in q or "생명" in q or "세포" in q:
            return "생명"
        if "기계" in q or "기술" in q or "로봇" in q:
            return "기술"
        if "집" in q or "학교" in q or "생활" in q:
            return "생활"
        if "비" in q or "바람" in q or "날씨" in q or "하늘" in q:
            return "자연"

        return DEFAULT_CATEGORY

    def _normalize_category(self, category: str) -> str:
        cleaned = category.strip()
        if cleaned in ALLOWED_CATEGORIES:
            return cleaned
        alias = {
            "nature": "자연",
            "life": "생활",
            "animal": "동물",
            "space": "우주",
            "science": "과학",
            "biology": "생명",
            "technology": "기술",
        }
        lowered = cleaned.lower()
        if lowered in alias:
            return alias[lowered]
        raise ValueError("지원하지 않는 분류입니다.")

    def _matches_keyword(self, item: CuriosityEntry, keyword: str) -> bool:
        if keyword in item.question.lower():
            return True
        if keyword in item.aiAnswer.lower():
            return True
        if keyword in item.topic.lower():
            return True
        for principle in item.discoveredPrinciples:
            if keyword in principle.lower():
                return True
        return False


def as_dict(entry: CuriosityEntry) -> dict:
    return asdict(entry)

from __future__ import annotations

from dataclasses import asdict, dataclass, field

FIELDS = ["물리", "화학", "생명과학"]

BASE_PRINCIPLES: dict[str, list[str]] = {
    "물리": ["중력", "마찰력", "관성", "공기 저항"],
    "화학": ["용해", "증발", "산화", "산·염기"],
    "생명과학": ["광합성", "세포", "호흡"],
}

TOPIC_TO_FIELD: dict[str, str] = {
    "얼음": "물리",
    "물": "화학",
    "거울": "물리",
    "구름": "화학",
    "전자레인지": "물리",
    "일반": "물리",
}


@dataclass
class DiscoveryItem:
    principle: str
    sourceTopic: str
    sourceSessionId: str | None = None


@dataclass
class FieldCatalog:
    fieldName: str
    baselinePrinciples: list[str] = field(default_factory=list)
    discoveredPrinciples: list[DiscoveryItem] = field(default_factory=list)


class ScienceCatalogService:
    def __init__(self) -> None:
        self._catalog: dict[str, FieldCatalog] = {
            field_name: FieldCatalog(fieldName=field_name, baselinePrinciples=BASE_PRINCIPLES[field_name][:])
            for field_name in FIELDS
        }

    def add_discovery(self, topic: str, principle: str, source_session_id: str | None = None) -> DiscoveryItem | None:
        clean = principle.strip()
        if not clean:
            return None

        field_name = self._resolve_field(topic=topic, principle=clean)
        field_catalog = self._catalog[field_name]

        for existing in field_catalog.discoveredPrinciples:
            if existing.principle == clean:
                if source_session_id and not existing.sourceSessionId:
                    existing.sourceSessionId = source_session_id
                return existing

        item = DiscoveryItem(principle=clean, sourceTopic=topic, sourceSessionId=source_session_id)
        field_catalog.discoveredPrinciples.append(item)
        return item

    def list_catalog(self, field_name: str | None = None) -> list[FieldCatalog]:
        if field_name:
            resolved = self._normalize_field(field_name)
            return [self._catalog[resolved]]
        return [self._catalog[name] for name in FIELDS]

    def search(self, keyword: str) -> list[dict]:
        token = keyword.strip().lower()
        if not token:
            return []

        matched: list[dict] = []
        for field_name in FIELDS:
            field_catalog = self._catalog[field_name]
            for base in field_catalog.baselinePrinciples:
                if token in base.lower():
                    matched.append(
                        {
                            "field": field_name,
                            "principle": base,
                            "kind": "baseline",
                            "sourceTopic": None,
                            "sourceSessionId": None,
                        }
                    )
            for discovered in field_catalog.discoveredPrinciples:
                if token in discovered.principle.lower() or token in discovered.sourceTopic.lower():
                    matched.append(
                        {
                            "field": field_name,
                            "principle": discovered.principle,
                            "kind": "discovered",
                            "sourceTopic": discovered.sourceTopic,
                            "sourceSessionId": discovered.sourceSessionId,
                        }
                    )
        return matched

    def _resolve_field(self, topic: str, principle: str) -> str:
        text = principle.lower()
        if any(token in text for token in ["용해", "증발", "산화", "산", "염기", "반응"]):
            return "화학"
        if any(token in text for token in ["세포", "광합성", "호흡", "생물", "식물", "동물"]):
            return "생명과학"
        if any(token in text for token in ["중력", "마찰", "관성", "공기 저항", "열", "빛", "반사", "밀도"]):
            return "물리"
        return TOPIC_TO_FIELD.get(topic, "물리")

    def _normalize_field(self, field_name: str) -> str:
        cleaned = field_name.strip()
        if cleaned in FIELDS:
            return cleaned

        alias = {
            "physics": "물리",
            "chemistry": "화학",
            "biology": "생명과학",
        }
        lowered = cleaned.lower()
        if lowered in alias:
            return alias[lowered]
        raise ValueError("지원하지 않는 분야입니다.")


def as_dict(catalog: FieldCatalog) -> dict:
    return {
        "fieldName": catalog.fieldName,
        "baselinePrinciples": catalog.baselinePrinciples[:],
        "discoveredPrinciples": [asdict(item) for item in catalog.discoveredPrinciples],
    }

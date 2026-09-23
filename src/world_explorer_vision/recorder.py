from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


@dataclass
class Measurement:
    name: str
    value: float
    unit: str
    at: str


@dataclass
class ExperimentRecord:
    sessionId: str
    title: str
    startPhotos: list[str]
    middlePhotos: list[str]
    endPhotos: list[str]
    observationNotes: list[str]
    measurements: list[Measurement]
    expectedResult: str
    actualResult: str
    updatedAt: str


class ExperimentRecordService:
    def __init__(self) -> None:
        self._records: dict[str, ExperimentRecord] = {}

    def init_record(self, session_id: str, title: str) -> ExperimentRecord:
        record = ExperimentRecord(
            sessionId=session_id,
            title=title,
            startPhotos=[],
            middlePhotos=[],
            endPhotos=[],
            observationNotes=[],
            measurements=[],
            expectedResult="",
            actualResult="",
            updatedAt=_now(),
        )
        self._records[session_id] = record
        return record

    def get_record(self, session_id: str) -> ExperimentRecord:
        if session_id not in self._records:
            raise ValueError("존재하지 않는 실험 기록입니다.")
        return self._records[session_id]

    def add_photo(self, session_id: str, stage: str, photo_ref: str) -> ExperimentRecord:
        record = self.get_record(session_id)
        if stage == "start":
            record.startPhotos.append(photo_ref)
        elif stage == "middle":
            record.middlePhotos.append(photo_ref)
        elif stage == "end":
            record.endPhotos.append(photo_ref)
        else:
            raise ValueError("사진 단계는 start, middle, end 중 하나여야 합니다.")
        record.updatedAt = _now()
        return record

    def add_observation(self, session_id: str, note: str) -> ExperimentRecord:
        record = self.get_record(session_id)
        record.observationNotes.append(note)
        record.updatedAt = _now()
        return record

    def add_measurement(self, session_id: str, name: str, value: float, unit: str) -> ExperimentRecord:
        record = self.get_record(session_id)
        record.measurements.append(
            Measurement(
                name=name,
                value=value,
                unit=unit,
                at=_now(),
            )
        )
        record.updatedAt = _now()
        return record

    def set_expected_result(self, session_id: str, text: str) -> ExperimentRecord:
        record = self.get_record(session_id)
        record.expectedResult = text
        record.updatedAt = _now()
        return record

    def set_actual_result(self, session_id: str, text: str) -> ExperimentRecord:
        record = self.get_record(session_id)
        record.actualResult = text
        record.updatedAt = _now()
        return record


def as_dict(record: ExperimentRecord) -> dict:
    return {
        "sessionId": record.sessionId,
        "title": record.title,
        "startPhotos": record.startPhotos,
        "middlePhotos": record.middlePhotos,
        "endPhotos": record.endPhotos,
        "observationNotes": record.observationNotes,
        "measurements": [asdict(item) for item in record.measurements],
        "expectedResult": record.expectedResult,
        "actualResult": record.actualResult,
        "updatedAt": record.updatedAt,
    }

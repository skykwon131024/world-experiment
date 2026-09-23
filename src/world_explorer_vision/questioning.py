from __future__ import annotations

from dataclasses import asdict, dataclass
import re
import uuid

from .knowledge import ALIASES, GENERIC_QUESTIONS, OBJECT_KNOWLEDGE, SIMPLE_EXPLANATIONS
from .explainer import ExplanationService, as_dict as explanation_as_dict
from .experimenter import ExperimentService, as_dict as experiment_as_dict
from .observer import ObservationService, as_dict as observation_as_dict
from .recorder import ExperimentRecordService, as_dict as record_as_dict
from .analyzer import ExperimentAnalysisService, as_dict as analysis_as_dict
from .recommender import RelatedQuestionService, as_dict as related_as_dict
from .vault import CuriosityVaultService, as_dict as vault_as_dict
from .catalog import ScienceCatalogService, as_dict as catalog_as_dict
from .today_curiosity import TodayCuriosityService, as_dict as today_as_dict
from .exploration_log import ExplorationLogService, as_dict as exploration_as_dict
from .recognizer import RecognitionService
from .step_guide import ExperimentStepGuideService, as_dict as step_guide_as_dict


WHITESPACE = re.compile(r"\s+")
ENDING = re.compile(r"[?.!]+$")


@dataclass
class QuestionInput:
    source: str
    questionText: str
    imageFileName: str | None = None
    imageHint: str | None = None


@dataclass
class QuestionResult:
    source: str
    normalizedQuestion: str
    interpretedTopic: str
    confidence: float
    answerPreview: str
    suggestedQuestions: list[str]
    explanation: dict
    observationPlan: dict
    experimentSuggestions: list[dict]
    relatedQuestions: list[str]
    vaultEntryId: str | None


@dataclass
class FollowUpTurn:
    role: str
    text: str


@dataclass
class FollowUpResult:
    threadId: str
    turnIndex: int
    question: str
    answer: str
    topic: str
    selectedLevel: str
    suggestedNextQuestions: list[str]
    historyCount: int


class QuestionService:
    def __init__(self, recognizer: RecognitionService) -> None:
        self.recognizer = recognizer
        self.explainer = ExplanationService()
        self.observer = ObservationService()
        self.experimenter = ExperimentService()
        self.step_guide = ExperimentStepGuideService()
        self.recorder = ExperimentRecordService()
        self.analyzer = ExperimentAnalysisService()
        self.recommender = RelatedQuestionService()
        self.vault = CuriosityVaultService()
        self.catalog = ScienceCatalogService()
        self.today_curiosity = TodayCuriosityService()
        self.exploration_log = ExplorationLogService()
        self._threads: dict[str, list[FollowUpTurn]] = {}
        self._thread_topic: dict[str, str] = {}

    def ask_text(self, question_text: str, level: str = "easy") -> QuestionResult:
        normalized = _normalize_question(question_text)
        topic, confidence = _infer_topic(normalized)
        result = _build_result(
            source="text",
            normalized_question=normalized,
            topic=topic,
            confidence=confidence,
            level=level,
            explainer=self.explainer,
            observer=self.observer,
            experimenter=self.experimenter,
            recommender=self.recommender,
        )
        entry_id = self._save_curiosity_entry(result=result, related_photos=None)
        result.vaultEntryId = entry_id
        return result

    def ask_voice(self, transcript: str, level: str = "easy") -> QuestionResult:
        # 음성 인식 결과 텍스트를 동일한 질문 파이프라인으로 보낸다.
        normalized = _normalize_question(transcript)
        topic, confidence = _infer_topic(normalized)
        result = _build_result(
            source="voice",
            normalized_question=normalized,
            topic=topic,
            confidence=confidence,
            level=level,
            explainer=self.explainer,
            observer=self.observer,
            experimenter=self.experimenter,
            recommender=self.recommender,
        )
        entry_id = self._save_curiosity_entry(result=result, related_photos=None)
        result.vaultEntryId = entry_id
        return result

    def ask_photo(
        self,
        image_file_name: str,
        question_text: str | None = None,
        image_hint: str | None = None,
        level: str = "easy",
    ) -> QuestionResult:
        recognition = self.recognizer.recognize(file_name=image_file_name, user_hint=image_hint)
        top_detection = recognition.detections[0]

        if question_text and question_text.strip():
            normalized = _normalize_question(question_text)
            inferred_topic, inferred_confidence = _infer_topic(normalized)
            if inferred_topic == "일반":
                inferred_topic = top_detection.name
                inferred_confidence = max(inferred_confidence, top_detection.confidence)
            topic = inferred_topic
            confidence = inferred_confidence
        else:
            auto_question = recognition.suggestedQuestions[0]
            normalized = _normalize_question(auto_question)
            topic = top_detection.name
            confidence = top_detection.confidence

        result = _build_result(
            source="photo",
            normalized_question=normalized,
            topic=topic,
            confidence=confidence,
            level=level,
            explainer=self.explainer,
            observer=self.observer,
            experimenter=self.experimenter,
            recommender=self.recommender,
        )

        if top_detection.name != "미확인 대상":
            result.suggestedQuestions = recognition.suggestedQuestions[:6]

        photo_refs = [image_file_name]
        entry_id = self._save_curiosity_entry(result=result, related_photos=photo_refs)
        result.vaultEntryId = entry_id

        return result

    def start_follow_up(self, first_question: str, level: str = "easy") -> FollowUpResult:
        normalized = _normalize_question(first_question)
        topic, _ = _infer_topic(normalized)
        if topic == "일반":
            topic = "얼음" if "얼음" in normalized else "일반"

        thread_id = str(uuid.uuid4())
        self._threads[thread_id] = [FollowUpTurn(role="user", text=normalized)]
        self._thread_topic[thread_id] = topic

        answer = self.explainer.explain(topic=topic, level=level).explanation
        self._threads[thread_id].append(FollowUpTurn(role="assistant", text=answer))
        self.vault.save(question=normalized, ai_answer=answer, topic=topic, source="follow_up")

        return FollowUpResult(
            threadId=thread_id,
            turnIndex=1,
            question=normalized,
            answer=answer,
            topic=topic,
            selectedLevel=self.explainer.normalize_level(level),
            suggestedNextQuestions=self._next_questions(topic=topic, last_question=normalized),
            historyCount=len(self._threads[thread_id]),
        )

    def ask_follow_up(self, thread_id: str, question_text: str, level: str = "easy") -> FollowUpResult:
        if thread_id not in self._threads:
            raise ValueError("존재하지 않는 대화 스레드입니다.")

        normalized = _normalize_question(question_text)
        inferred_topic, _ = _infer_topic(normalized)
        topic = self._thread_topic.get(thread_id, "일반")
        if inferred_topic != "일반":
            topic = inferred_topic
            self._thread_topic[thread_id] = topic

        answer = self.explainer.explain(topic=topic, level=level).explanation

        self._threads[thread_id].append(FollowUpTurn(role="user", text=normalized))
        self._threads[thread_id].append(FollowUpTurn(role="assistant", text=answer))
        self.vault.save(question=normalized, ai_answer=answer, topic=topic, source="follow_up")

        turn_index = len(self._threads[thread_id]) // 2
        return FollowUpResult(
            threadId=thread_id,
            turnIndex=turn_index,
            question=normalized,
            answer=answer,
            topic=topic,
            selectedLevel=self.explainer.normalize_level(level),
            suggestedNextQuestions=self._next_questions(topic=topic, last_question=normalized),
            historyCount=len(self._threads[thread_id]),
        )

    def get_follow_up_history(self, thread_id: str) -> list[dict]:
        if thread_id not in self._threads:
            return []
        return [asdict(turn) for turn in self._threads[thread_id]]

    def create_observation_plan(self, question_text: str) -> dict:
        normalized = _normalize_question(question_text)
        topic, confidence = _infer_topic(normalized)
        plan = self.observer.create_plan(topic)
        return {
            "question": normalized,
            "topic": topic,
            "confidence": round(confidence, 2),
            "plan": observation_as_dict(plan),
        }

    def create_experiment_suggestions(self, question_text: str, available_items: list[str] | None = None) -> dict:
        normalized = _normalize_question(question_text)
        topic, confidence = _infer_topic(normalized)
        plans = self.experimenter.suggest(topic=topic, available_items=available_items, limit=3)
        return {
            "question": normalized,
            "topic": topic,
            "confidence": round(confidence, 2),
            "availableItems": available_items or [],
            "experiments": [experiment_as_dict(p) for p in plans],
        }

    def start_experiment_guide(
        self,
        question_text: str,
        available_items: list[str] | None = None,
        selected_index: int = 0,
    ) -> dict:
        suggestions = self.create_experiment_suggestions(question_text, available_items)
        experiments = suggestions["experiments"]
        if not experiments:
            raise ValueError("시작할 실험이 없습니다.")

        index = max(0, min(selected_index, len(experiments) - 1))
        selected = experiments[index]
        plan = self.experimenter.suggest(
            topic=suggestions["topic"],
            available_items=available_items,
            limit=max(index + 1, 1),
        )[index]

        state = self.step_guide.start(plan)
        self.recorder.init_record(session_id=state.sessionId, title=plan.title)
        self.vault.attach_experiment_by_topic(topic=suggestions["topic"], experiment_session_id=state.sessionId)
        return {
            "question": suggestions["question"],
            "topic": suggestions["topic"],
            "selectedExperiment": selected,
            "guide": step_guide_as_dict(state),
        }

    def complete_experiment_step(self, session_id: str) -> dict:
        state = self.step_guide.complete_current_step(session_id)
        return step_guide_as_dict(state)

    def get_experiment_guide(self, session_id: str) -> dict:
        state = self.step_guide.get(session_id)
        return step_guide_as_dict(state)

    def submit_experiment_result(self, session_id: str) -> dict:
        state = self.step_guide.submit_result(session_id)
        return step_guide_as_dict(state)

    def add_experiment_photo(self, session_id: str, stage: str, photo_ref: str) -> dict:
        record = self.recorder.add_photo(session_id=session_id, stage=stage, photo_ref=photo_ref)
        return record_as_dict(record)

    def add_experiment_observation(self, session_id: str, note: str) -> dict:
        record = self.recorder.add_observation(session_id=session_id, note=note)
        return record_as_dict(record)

    def add_experiment_measurement(self, session_id: str, name: str, value: float, unit: str) -> dict:
        record = self.recorder.add_measurement(session_id=session_id, name=name, value=value, unit=unit)
        return record_as_dict(record)

    def set_experiment_expected_result(self, session_id: str, text: str) -> dict:
        record = self.recorder.set_expected_result(session_id=session_id, text=text)
        return record_as_dict(record)

    def set_experiment_actual_result(self, session_id: str, text: str) -> dict:
        record = self.recorder.set_actual_result(session_id=session_id, text=text)
        return record_as_dict(record)

    def get_experiment_record(self, session_id: str) -> dict:
        record = self.recorder.get_record(session_id=session_id)
        return record_as_dict(record)

    def analyze_experiment_result(self, session_id: str, topic: str | None = None) -> dict:
        record = self.recorder.get_record(session_id=session_id)
        resolved_topic = topic or _infer_topic_from_text(record.title)
        next_plans = self.experimenter.suggest(topic=resolved_topic, available_items=None, limit=2)
        analysis = self.analyzer.analyze(record=record, topic=resolved_topic, next_plans=next_plans)
        self.vault.add_discovered_principle_by_topic(topic=resolved_topic, principle=analysis.sciencePrinciple)
        self.catalog.add_discovery(
            topic=resolved_topic,
            principle=analysis.sciencePrinciple,
            source_session_id=session_id,
        )

        return {
            "sessionId": session_id,
            "title": record.title,
            "analysis": analysis_as_dict(analysis),
        }

    def get_science_catalog(self, field_name: str | None = None) -> dict:
        catalogs = self.catalog.list_catalog(field_name=field_name)
        return {
            "count": len(catalogs),
            "catalog": [catalog_as_dict(item) for item in catalogs],
        }

    def search_science_catalog(self, keyword: str) -> dict:
        found = self.catalog.search(keyword=keyword)
        return {
            "keyword": keyword,
            "count": len(found),
            "results": found,
        }

    def get_today_curiosity(self, limit: int = 1) -> dict:
        entries = self.vault.list_entries()
        recommendations = self.today_curiosity.recommend(entries=entries, limit=limit)
        return {
            "count": len(recommendations),
            "items": [today_as_dict(item) for item in recommendations],
        }

    def choose_today_curiosity_action(self, question_text: str, action: str, level: str = "easy") -> dict:
        normalized_action = action.strip()
        if normalized_action == "알아보기":
            result = self.ask_text(question_text, level=level)
            return {
                "action": normalized_action,
                "mode": "explain",
                "result": as_dict(result),
            }

        if normalized_action == "직접 확인하기":
            observation = self.create_observation_plan(question_text)
            experiments = self.create_experiment_suggestions(question_text, available_items=None)
            return {
                "action": normalized_action,
                "mode": "observe",
                "observationPlan": observation,
                "experimentSuggestions": experiments,
            }

        raise ValueError("지원하지 않는 선택입니다. '알아보기' 또는 '직접 확인하기'를 사용하세요.")

    def get_exploration_record(self) -> dict:
        vault_entries = self.vault.list_entries()
        experiment_sessions = self.step_guide.list_sessions()
        catalogs = self.catalog.list_catalog()
        record = self.exploration_log.build(
            vault_entries=vault_entries,
            experiment_sessions=experiment_sessions,
            catalogs=catalogs,
        )
        return exploration_as_dict(record)

    def get_curiosity_vault(self, category: str | None = None, keyword: str | None = None) -> dict:
        entries = self.vault.list_entries(category=category, keyword=keyword)
        return {
            "count": len(entries),
            "entries": [vault_as_dict(entry) for entry in entries],
        }

    def update_curiosity_category(self, entry_id: str, new_category: str) -> dict:
        updated = self.vault.update_category(entry_id=entry_id, new_category=new_category)
        return vault_as_dict(updated)

    def search_curiosity_vault(self, keyword: str) -> dict:
        entries = self.vault.search(keyword=keyword)
        return {
            "keyword": keyword,
            "count": len(entries),
            "entries": [vault_as_dict(entry) for entry in entries],
        }

    def recommend_related_questions(self, current_question: str, limit: int = 4) -> dict:
        normalized = _normalize_question(current_question)
        topic, confidence = _infer_topic(normalized)
        result = self.recommender.recommend(topic=topic, current_question=normalized, limit=limit)
        payload = related_as_dict(result)
        payload["confidence"] = round(confidence, 2)
        return payload

    def _next_questions(self, topic: str, last_question: str) -> list[str]:
        if topic in OBJECT_KNOWLEDGE:
            base = OBJECT_KNOWLEDGE[topic].questions[:]
        else:
            base = GENERIC_QUESTIONS[:]

        filtered = [q for q in base if q != last_question]
        if topic != "일반":
            filtered.append(f"{topic}와 관련해 직접 확인해볼 방법은 무엇일까요?")
        else:
            filtered.append("이 현상을 확인하려면 어떤 조건을 바꿔보면 좋을까요?")
        return filtered[:4]

    def _save_curiosity_entry(self, result: QuestionResult, related_photos: list[str] | None) -> str:
        detail = result.explanation.get("explanation", result.answerPreview)
        entry = self.vault.save(
            question=result.normalizedQuestion,
            ai_answer=detail,
            topic=result.interpretedTopic,
            source=result.source,
            related_photos=related_photos,
            discovered_principles=[],
        )
        return entry.entryId


def _normalize_question(text: str) -> str:
    cleaned = WHITESPACE.sub(" ", text.strip())
    cleaned = ENDING.sub("", cleaned)
    if not cleaned:
        return "무엇이 궁금한지 알려주세요?"
    if not cleaned.endswith("?"):
        cleaned = f"{cleaned}?"
    return cleaned


def _infer_topic(normalized_question: str) -> tuple[str, float]:
    lower = normalized_question.lower()

    for ko_name in OBJECT_KNOWLEDGE.keys():
        if ko_name in normalized_question:
            return ko_name, 0.9

    for token, ko_name in ALIASES.items():
        if token in lower:
            return ko_name, 0.82

    return "일반", 0.55


def _infer_topic_from_text(text: str) -> str:
    for ko_name in OBJECT_KNOWLEDGE.keys():
        if ko_name in text:
            return ko_name
    return "일반"


def _build_result(
    source: str,
    normalized_question: str,
    topic: str,
    confidence: float,
    level: str,
    explainer: ExplanationService,
    observer: ObservationService,
    experimenter: ExperimentService,
    recommender: RelatedQuestionService,
) -> QuestionResult:
    if topic in OBJECT_KNOWLEDGE:
        suggested = OBJECT_KNOWLEDGE[topic].questions[:3]
    else:
        suggested = GENERIC_QUESTIONS

    answer_preview = SIMPLE_EXPLANATIONS.get(
        topic,
        "좋은 질문이에요. 먼저 눈에 보이는 변화를 관찰하고, 조건을 하나씩 바꿔 확인해볼 수 있어요.",
    )

    explanation = explanation_as_dict(explainer.explain(topic=topic, level=level))
    observation_plan = observation_as_dict(observer.create_plan(topic=topic))
    experiments = [experiment_as_dict(p) for p in experimenter.suggest(topic=topic, available_items=None, limit=2)]
    related = recommender.recommend(topic=topic, current_question=normalized_question, limit=4).relatedQuestions

    return QuestionResult(
        source=source,
        normalizedQuestion=normalized_question,
        interpretedTopic=topic,
        confidence=round(confidence, 2),
        answerPreview=answer_preview,
        suggestedQuestions=suggested,
        explanation=explanation,
        observationPlan=observation_plan,
        experimentSuggestions=experiments,
        relatedQuestions=related,
        vaultEntryId=None,
    )


def as_dict(result: QuestionResult) -> dict:
    return asdict(result)


def follow_up_as_dict(result: FollowUpResult) -> dict:
    return asdict(result)

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .external_client import ExternalApiClient, ExternalApiConfig, ExternalApiError, load_environment_file
from .azure_openai_client import AzureOpenAIClient, AzureOpenAIConfig
from .questioning import QuestionService, as_dict, follow_up_as_dict
from .recognizer import RecognitionService, as_api_dict
from .response_adapter import normalize_question_response


app = FastAPI(
    title="세상 실험가 API",
    version="0.2.0",
    description="세상 실험가 앱 기능(6.1~6.14) 로컬 실행용 API",
)

feedback_path = Path("data/recognition_feedback.jsonl")
recognizer_service = RecognitionService(feedback_file=feedback_path)
question_service = QuestionService(recognizer=recognizer_service)

workspace_root = Path(__file__).resolve().parents[2]
web_root = workspace_root / "web"
assets_root = web_root / "assets"
load_environment_file(workspace_root / ".env")
external_config = ExternalApiConfig.from_environment(env_file=workspace_root / ".env")
external_client = ExternalApiClient(config=external_config)
azure_openai_config = AzureOpenAIConfig.from_environment(env_file=workspace_root / ".env")
azure_openai_client = AzureOpenAIClient(config=azure_openai_config)

if assets_root.exists():
    app.mount("/assets", StaticFiles(directory=assets_root), name="assets")


class CorrectionRequest(BaseModel):
    requestId: str = Field(..., min_length=1)
    originalName: str = Field(..., min_length=1)
    correctedName: str = Field(..., min_length=1)
    note: str | None = None


class TextQuestionRequest(BaseModel):
    questionText: str = Field(..., min_length=1)
    level: str = "easy"


class VoiceQuestionRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    level: str = "easy"


class FollowUpStartRequest(BaseModel):
    questionText: str = Field(..., min_length=1)
    level: str = "easy"


class FollowUpAskRequest(BaseModel):
    questionText: str = Field(..., min_length=1)
    level: str = "easy"


class ObservationPlanRequest(BaseModel):
    questionText: str = Field(..., min_length=1)


class ExperimentSuggestionRequest(BaseModel):
    questionText: str = Field(..., min_length=1)
    availableItems: list[str] | None = None


class ExperimentGuideStartRequest(BaseModel):
    questionText: str = Field(..., min_length=1)
    availableItems: list[str] | None = None
    selectedIndex: int = 0


class ExperimentPhotoRequest(BaseModel):
    stage: str = Field(..., min_length=1)
    photoRef: str = Field(..., min_length=1)


class ExperimentObservationRequest(BaseModel):
    note: str = Field(..., min_length=1)


class ExperimentMeasurementRequest(BaseModel):
    name: str = Field(..., min_length=1)
    value: float
    unit: str = Field(..., min_length=1)


class ExperimentResultTextRequest(BaseModel):
    text: str = Field(..., min_length=1)


class AnalyzeRequest(BaseModel):
    topic: str | None = None


class RelatedQuestionRequest(BaseModel):
    currentQuestion: str = Field(..., min_length=1)
    limit: int = 4


class VaultCategoryUpdateRequest(BaseModel):
    newCategory: str = Field(..., min_length=1)


class TodayActionRequest(BaseModel):
    questionText: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    level: str = "easy"


@app.get("/")
def root():
    index_file = web_root / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"detail": "web/index.html 파일이 없습니다."}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config/status")
def config_status() -> dict:
    return {
        "externalEndpointConfigured": bool(external_config.endpoint),
        "apiKeyConfigured": bool(external_config.api_key),
        "apiKeyHeader": external_config.api_key_header,
        "apiKeyPrefix": external_config.api_key_prefix,
        "provider": _provider(),
        "azureOpenAIConfigured": azure_openai_config.is_configured,
        "azureOpenAIApiKeyConfigured": bool(azure_openai_config.api_key),
        "azureOpenAIDeploymentConfigured": bool(azure_openai_config.deployment),
        "azureOpenAIApiVersion": azure_openai_config.api_version,
        "questionPaths": _external_paths(),
        "message": "설정이 있으면 질문/사진/음성 요청을 외부 API로 전달합니다.",
    }


@app.post("/v1/recognize")
async def recognize(
    image: UploadFile = File(...),
    userHint: str | None = Form(default=None),
) -> dict:
    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")

    file_name = image.filename or "unknown"
    result = recognizer_service.recognize(file_name=file_name, user_hint=userHint)

    return {
        "target": "사물·현상 인식",
        "result": as_api_dict(result),
    }


@app.post("/v1/recognize/correction")
def save_correction(payload: CorrectionRequest) -> dict[str, str]:
    recognizer_service.save_correction(
        request_id=payload.requestId,
        original_name=payload.originalName,
        corrected_name=payload.correctedName,
        note=payload.note,
    )
    return {"message": "인식 수정이 저장되었습니다."}


@app.post("/api/v1/questions/text")
def ask_text(payload: TextQuestionRequest) -> dict:
    external = _forward_text_question(payload)
    if external is not None:
        return external

    result = question_service.ask_text(question_text=payload.questionText, level=payload.level)
    return as_dict(result)


@app.post("/api/v1/questions/voice")
def ask_voice(payload: VoiceQuestionRequest) -> dict:
    external = _forward_voice_question(payload)
    if external is not None:
        return external

    result = question_service.ask_voice(transcript=payload.transcript, level=payload.level)
    return as_dict(result)


@app.post("/api/v1/questions/photo")
async def ask_photo(
    image: UploadFile = File(...),
    questionText: str | None = Form(default=None),
    imageHint: str | None = Form(default=None),
    level: str = Form(default="easy"),
) -> dict:
    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")

    file_name = image.filename or "unknown"
    image_content = await image.read()
    external = _forward_photo_question(
        file_name=file_name,
        image_content=image_content,
        content_type=image.content_type or "application/octet-stream",
        question_text=questionText,
        image_hint=imageHint,
        level=level,
    )
    if external is not None:
        return external

    result = question_service.ask_photo(
        image_file_name=file_name,
        question_text=questionText,
        image_hint=imageHint,
        level=level,
    )
    return as_dict(result)


@app.post("/api/v1/questions/follow-up/start")
def start_follow_up(payload: FollowUpStartRequest) -> dict:
    result = question_service.start_follow_up(first_question=payload.questionText, level=payload.level)
    return follow_up_as_dict(result)


@app.post("/api/v1/questions/follow-up/{thread_id}")
def ask_follow_up(thread_id: str, payload: FollowUpAskRequest) -> dict:
    try:
        result = question_service.ask_follow_up(thread_id=thread_id, question_text=payload.questionText, level=payload.level)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return follow_up_as_dict(result)


@app.get("/api/v1/questions/follow-up/{thread_id}/history")
def follow_up_history(thread_id: str) -> dict:
    return {
        "threadId": thread_id,
        "history": question_service.get_follow_up_history(thread_id),
    }


@app.post("/api/v1/observation/plan")
def create_observation_plan(payload: ObservationPlanRequest) -> dict:
    return question_service.create_observation_plan(question_text=payload.questionText)


@app.post("/api/v1/experiments/suggestions")
def create_experiment_suggestions(payload: ExperimentSuggestionRequest) -> dict:
    return question_service.create_experiment_suggestions(
        question_text=payload.questionText,
        available_items=payload.availableItems,
    )


@app.post("/api/v1/experiments/guide/start")
def start_experiment_guide(payload: ExperimentGuideStartRequest) -> dict:
    try:
        return question_service.start_experiment_guide(
            question_text=payload.questionText,
            available_items=payload.availableItems,
            selected_index=payload.selectedIndex,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/experiments/guide/{session_id}/step/complete")
def complete_experiment_step(session_id: str) -> dict:
    try:
        return question_service.complete_experiment_step(session_id=session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/v1/experiments/guide/{session_id}")
def get_experiment_guide(session_id: str) -> dict:
    try:
        return question_service.get_experiment_guide(session_id=session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/experiments/guide/{session_id}/result/submit")
def submit_experiment_result(session_id: str) -> dict:
    try:
        return question_service.submit_experiment_result(session_id=session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/experiments/record/{session_id}/photo")
def add_experiment_photo(session_id: str, payload: ExperimentPhotoRequest) -> dict:
    try:
        return question_service.add_experiment_photo(session_id=session_id, stage=payload.stage, photo_ref=payload.photoRef)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/experiments/record/{session_id}/observation")
def add_experiment_observation(session_id: str, payload: ExperimentObservationRequest) -> dict:
    try:
        return question_service.add_experiment_observation(session_id=session_id, note=payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/experiments/record/{session_id}/measurement")
def add_experiment_measurement(session_id: str, payload: ExperimentMeasurementRequest) -> dict:
    try:
        return question_service.add_experiment_measurement(
            session_id=session_id,
            name=payload.name,
            value=payload.value,
            unit=payload.unit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/experiments/record/{session_id}/expected")
def set_experiment_expected(session_id: str, payload: ExperimentResultTextRequest) -> dict:
    try:
        return question_service.set_experiment_expected_result(session_id=session_id, text=payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/experiments/record/{session_id}/actual")
def set_experiment_actual(session_id: str, payload: ExperimentResultTextRequest) -> dict:
    try:
        return question_service.set_experiment_actual_result(session_id=session_id, text=payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/v1/experiments/record/{session_id}")
def get_experiment_record(session_id: str) -> dict:
    try:
        return question_service.get_experiment_record(session_id=session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/experiments/record/{session_id}/analyze")
def analyze_experiment_record(session_id: str, payload: AnalyzeRequest) -> dict:
    try:
        return question_service.analyze_experiment_result(session_id=session_id, topic=payload.topic)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/questions/related")
def recommend_related_questions(payload: RelatedQuestionRequest) -> dict:
    return question_service.recommend_related_questions(current_question=payload.currentQuestion, limit=payload.limit)


@app.get("/api/v1/vault")
def get_vault(
    category: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
) -> dict:
    return question_service.get_curiosity_vault(category=category, keyword=keyword)


@app.get("/api/v1/vault/search")
def search_vault(keyword: str = Query(..., min_length=1)) -> dict:
    return question_service.search_curiosity_vault(keyword=keyword)


@app.patch("/api/v1/vault/{entry_id}/category")
def update_vault_category(entry_id: str, payload: VaultCategoryUpdateRequest) -> dict:
    try:
        return question_service.update_curiosity_category(entry_id=entry_id, new_category=payload.newCategory)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/v1/catalog")
def get_catalog(fieldName: str | None = Query(default=None)) -> dict:
    try:
        return question_service.get_science_catalog(field_name=fieldName)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/v1/catalog/search")
def search_catalog(keyword: str = Query(..., min_length=1)) -> dict:
    return question_service.search_science_catalog(keyword=keyword)


@app.get("/api/v1/today")
def get_today(limit: int = Query(default=1, ge=1, le=5)) -> dict:
    return question_service.get_today_curiosity(limit=limit)


@app.post("/api/v1/today/action")
def choose_today_action(payload: TodayActionRequest) -> dict:
    try:
        return question_service.choose_today_curiosity_action(
            question_text=payload.questionText,
            action=payload.action,
            level=payload.level,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/v1/exploration-record")
def get_exploration_record() -> dict:
    return question_service.get_exploration_record()


def _external_paths() -> dict[str, str]:
    return {
        "text": _environment_value("WORLD_EXPLORER_TEXT_PATH", "/questions/text"),
        "voice": _environment_value("WORLD_EXPLORER_VOICE_PATH", "/questions/voice"),
        "photo": _environment_value("WORLD_EXPLORER_PHOTO_PATH", "/questions/photo"),
    }


def _forward_text_question(payload: TextQuestionRequest) -> dict | None:
    if _provider() == "azure_openai":
        try:
            response = azure_openai_client.ask_text(question=payload.questionText, level=payload.level)
        except ExternalApiError as exc:
            raise _external_http_exception(exc) from exc
        return normalize_question_response(response, "text", payload.questionText, payload.level)

    if not external_config.is_configured:
        return None

    try:
        response = external_client.post_json(
            path=_external_paths()["text"],
            payload={"questionText": payload.questionText, "level": payload.level},
        )
    except ExternalApiError as exc:
        raise _external_http_exception(exc) from exc
    return normalize_question_response(
        response=response,
        source="text",
        question=payload.questionText,
        level=payload.level,
    )


def _forward_voice_question(payload: VoiceQuestionRequest) -> dict | None:
    if _provider() == "azure_openai":
        try:
            response = azure_openai_client.ask_voice(transcript=payload.transcript, level=payload.level)
        except ExternalApiError as exc:
            raise _external_http_exception(exc) from exc
        return normalize_question_response(response, "voice", payload.transcript, payload.level)

    if not external_config.is_configured:
        return None

    try:
        response = external_client.post_json(
            path=_external_paths()["voice"],
            payload={"transcript": payload.transcript, "level": payload.level},
        )
    except ExternalApiError as exc:
        raise _external_http_exception(exc) from exc
    return normalize_question_response(
        response=response,
        source="voice",
        question=payload.transcript,
        level=payload.level,
    )


def _forward_photo_question(
    file_name: str,
    image_content: bytes,
    content_type: str,
    question_text: str | None,
    image_hint: str | None,
    level: str,
) -> dict | None:
    if _provider() == "azure_openai":
        try:
            response = azure_openai_client.ask_photo(
                image_content=image_content,
                content_type=content_type,
                question=question_text,
                image_hint=image_hint,
                level=level,
            )
        except ExternalApiError as exc:
            raise _external_http_exception(exc) from exc
        return normalize_question_response(response, "photo", question_text or file_name, level)

    if not external_config.is_configured:
        return None

    fields = {"level": level}
    if question_text:
        fields["questionText"] = question_text
    if image_hint:
        fields["imageHint"] = image_hint

    try:
        response = external_client.post_multipart(
            path=_external_paths()["photo"],
            fields=fields,
            file_field="image",
            file_name=file_name,
            file_content=image_content,
            content_type=content_type,
        )
    except ExternalApiError as exc:
        raise _external_http_exception(exc) from exc
    return normalize_question_response(
        response=response,
        source="photo",
        question=question_text or file_name,
        level=level,
    )


def _external_http_exception(exc: ExternalApiError) -> HTTPException:
    status_code = exc.status_code if exc.status_code and 400 <= exc.status_code < 600 else 502
    return HTTPException(
        status_code=status_code,
        detail={"message": str(exc), "externalStatusCode": exc.status_code},
    )


def _environment_value(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is not None:
        return value.strip() or default

    env_file = workspace_root / ".env"
    if env_file.exists():
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, raw_value = line.split("=", 1)
            if key.strip() == name:
                return raw_value.strip().strip('"').strip("'") or default
    return default


def _provider() -> str:
    return _environment_value("WORLD_EXPLORER_PROVIDER", "generic")

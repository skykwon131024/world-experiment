from __future__ import annotations

import base64
from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any
from urllib import error, request

from .external_client import ExternalApiError


@dataclass(frozen=True)
class AzureOpenAIConfig:
    endpoint: str
    api_key: str
    deployment: str
    api_version: str = "2024-10-21"
    timeout_seconds: float = 30.0

    @classmethod
    def from_environment(cls, env_file: str | Path | None = None) -> AzureOpenAIConfig:
        values = _read_env(env_file)
        return cls(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", values.get("AZURE_OPENAI_ENDPOINT", "")).strip().rstrip("/"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY", values.get("AZURE_OPENAI_API_KEY", "")).strip(),
            deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", values.get("AZURE_OPENAI_DEPLOYMENT", "")).strip(),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", values.get("AZURE_OPENAI_API_VERSION", "2024-10-21")).strip(),
            timeout_seconds=float(os.getenv("AZURE_OPENAI_TIMEOUT_SECONDS", values.get("AZURE_OPENAI_TIMEOUT_SECONDS", "30"))),
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key and self.deployment and self.api_version)

    def require_configured(self) -> None:
        missing = []
        if not self.endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not self.api_key:
            missing.append("AZURE_OPENAI_API_KEY")
        if not self.deployment:
            missing.append("AZURE_OPENAI_DEPLOYMENT")
        if not self.api_version:
            missing.append("AZURE_OPENAI_API_VERSION")
        if missing:
            raise ExternalApiError(f"Azure OpenAI 설정이 부족합니다: {', '.join(missing)}")
        if self.timeout_seconds <= 0:
            raise ExternalApiError("AZURE_OPENAI_TIMEOUT_SECONDS는 0보다 커야 합니다.")


class AzureOpenAIClient:
    def __init__(self, config: AzureOpenAIConfig | None = None) -> None:
        self.config = config or AzureOpenAIConfig.from_environment()

    def ask_text(self, question: str, level: str = "easy") -> dict[str, Any]:
        return self._chat(
            messages=[
                {"role": "system", "content": "너는 세상 실험가의 탐구 코치다. 쉽고 정확하게 설명하고 직접 확인할 방법도 제안한다."},
                {"role": "user", "content": f"설명 수준: {level}\n질문: {question}"},
            ]
        )

    def ask_voice(self, transcript: str, level: str = "easy") -> dict[str, Any]:
        return self.ask_text(transcript, level=level)

    def ask_photo(
        self,
        image_content: bytes,
        content_type: str,
        question: str | None = None,
        image_hint: str | None = None,
        level: str = "easy",
    ) -> dict[str, Any]:
        image_data = base64.b64encode(image_content).decode("ascii")
        prompt = question or "사진 속 사물이나 현상을 관찰하고, 무엇인지와 궁금해할 만한 점을 설명해줘."
        if image_hint:
            prompt = f"사진 힌트: {image_hint}\n{prompt}"
        messages = [
            {"role": "system", "content": "너는 사진을 바탕으로 관찰을 돕는 세상 실험가의 탐구 코치다."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"설명 수준: {level}\n{prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:{content_type};base64,{image_data}"}},
                ],
            },
        ]
        return self._chat(messages=messages)

    def _chat(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        self.config.require_configured()
        if self._uses_responses_api():
            url = self.config.endpoint
            body_payload = {
                "model": self.config.deployment,
                "input": self._responses_input(messages),
            }
        else:
            url = (
                f"{self.config.endpoint}/openai/deployments/{self.config.deployment}"
                f"/chat/completions?api-version={self.config.api_version}"
            )
            body_payload = {"messages": messages}

        body = json.dumps(body_payload, ensure_ascii=False).encode("utf-8")
        http_request = request.Request(
            url=url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "api-key": self.config.api_key,
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self.config.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ExternalApiError(
                f"Azure OpenAI가 HTTP {exc.code} 오류를 반환했습니다.",
                status_code=exc.code,
                response_body=detail[:2000],
            ) from exc
        except error.URLError as exc:
            raise ExternalApiError(f"Azure OpenAI에 연결하지 못했습니다: {exc.reason}") from exc
        except TimeoutError as exc:
            raise ExternalApiError("Azure OpenAI 요청 시간이 초과되었습니다.") from exc

    def _uses_responses_api(self) -> bool:
        return self.config.endpoint.rstrip("/").endswith("/openai/v1/responses")

    def _responses_input(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        converted: list[dict[str, Any]] = []
        for message in messages:
            content = message.get("content")
            if isinstance(content, list):
                items = []
                for item in content:
                    if item.get("type") == "text":
                        items.append({"type": "input_text", "text": item.get("text", "")})
                    elif item.get("type") == "image_url":
                        items.append({"type": "input_image", "image_url": item.get("image_url", {}).get("url", "")})
                converted.append({"role": message.get("role", "user"), "content": items})
            else:
                converted.append({"role": message.get("role", "user"), "content": content or ""})
        return converted


def _read_env(env_file: str | Path | None) -> dict[str, str]:
    path = Path(env_file) if env_file else Path.cwd() / ".env"
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any
from urllib import error, parse, request


class ExternalApiError(RuntimeError):
    """외부 API 요청이 실패했을 때 사용하는 오류입니다."""

    def __init__(self, message: str, status_code: int | None = None, response_body: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


@dataclass(frozen=True)
class ExternalApiConfig:
    endpoint: str
    api_key: str
    api_key_header: str = "Authorization"
    api_key_prefix: str = "Bearer"
    timeout_seconds: float = 30.0

    @classmethod
    def from_environment(cls, env_file: str | Path | None = None) -> ExternalApiConfig:
        values = load_environment_file(env_file)
        endpoint = os.getenv("WORLD_EXPLORER_EXTERNAL_ENDPOINT", values.get("WORLD_EXPLORER_EXTERNAL_ENDPOINT", "")).strip()
        api_key = os.getenv("WORLD_EXPLORER_API_KEY", values.get("WORLD_EXPLORER_API_KEY", "")).strip()
        header = os.getenv(
            "WORLD_EXPLORER_API_KEY_HEADER",
            values.get("WORLD_EXPLORER_API_KEY_HEADER", "Authorization"),
        ).strip()
        prefix = os.getenv(
            "WORLD_EXPLORER_API_KEY_PREFIX",
            values.get("WORLD_EXPLORER_API_KEY_PREFIX", "Bearer"),
        ).strip()
        timeout_text = os.getenv(
            "WORLD_EXPLORER_EXTERNAL_TIMEOUT_SECONDS",
            values.get("WORLD_EXPLORER_EXTERNAL_TIMEOUT_SECONDS", "30"),
        ).strip()

        try:
            timeout = float(timeout_text)
        except ValueError as exc:
            raise ValueError("WORLD_EXPLORER_EXTERNAL_TIMEOUT_SECONDS는 숫자여야 합니다.") from exc

        if timeout <= 0:
            raise ValueError("외부 API 시간 제한은 0보다 커야 합니다.")

        return cls(
            endpoint=endpoint.rstrip("/"),
            api_key=api_key,
            api_key_header=header or "Authorization",
            api_key_prefix=prefix,
            timeout_seconds=timeout,
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key)

    def require_configured(self) -> None:
        if not self.endpoint:
            raise ExternalApiError("외부 API 주소가 설정되지 않았습니다.")
        if not self.api_key:
            raise ExternalApiError("외부 API 키가 설정되지 않았습니다.")


class ExternalApiClient:
    """주소와 인증 방식이 정해지면 여러 외부 API에 재사용하는 공통 연결기입니다."""

    def __init__(self, config: ExternalApiConfig | None = None) -> None:
        self.config = config or ExternalApiConfig.from_environment()

    def request_json(
        self,
        method: str,
        path: str = "",
        payload: dict[str, Any] | list[Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        body = None
        merged_headers = self._headers(headers)
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            merged_headers.setdefault("Content-Type", "application/json")

        response_body = self._request(method=method, path=path, body=body, headers=merged_headers)
        if not response_body:
            return None

        try:
            return json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise ExternalApiError("외부 API가 JSON이 아닌 응답을 보냈습니다.", response_body=response_body[:1000]) from exc

    def post_json(
        self,
        path: str = "",
        payload: dict[str, Any] | list[Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        return self.request_json(method="POST", path=path, payload=payload, headers=headers)

    def post_multipart(
        self,
        path: str,
        fields: dict[str, str] | None = None,
        file_field: str = "file",
        file_name: str = "upload.bin",
        file_content: bytes = b"",
        content_type: str = "application/octet-stream",
        headers: dict[str, str] | None = None,
    ) -> Any:
        boundary = "----WorldExplorerBoundary"
        chunks: list[bytes] = []
        for name, value in (fields or {}).items():
            chunks.extend(
                [
                    f"--{boundary}\r\n".encode(),
                    f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                    str(value).encode("utf-8"),
                    b"\r\n",
                ]
            )
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{file_field}"; filename="{file_name}"\r\n'.encode(),
                f"Content-Type: {content_type}\r\n\r\n".encode(),
                file_content,
                b"\r\n",
                f"--{boundary}--\r\n".encode(),
            ]
        )

        merged_headers = self._headers(headers)
        merged_headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        response_body = self._request(method="POST", path=path, body=b"".join(chunks), headers=merged_headers)
        if not response_body:
            return None
        try:
            return json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise ExternalApiError("외부 API가 JSON이 아닌 응답을 보냈습니다.", response_body=response_body[:1000]) from exc

    def _request(self, method: str, path: str, body: bytes | None, headers: dict[str, str]) -> str:
        self.config.require_configured()
        url = self._build_url(path)
        http_request = request.Request(url=url, data=body, headers=headers, method=method.upper())

        try:
            with request.urlopen(http_request, timeout=self.config.timeout_seconds) as response:
                return response.read().decode("utf-8")
        except error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            raise ExternalApiError(
                f"외부 API가 HTTP {exc.code} 오류를 반환했습니다.",
                status_code=exc.code,
                response_body=response_body[:2000],
            ) from exc
        except error.URLError as exc:
            raise ExternalApiError(f"외부 API에 연결하지 못했습니다: {exc.reason}") from exc
        except TimeoutError as exc:
            raise ExternalApiError("외부 API 요청 시간이 초과되었습니다.") from exc

    def _build_url(self, path: str) -> str:
        if not path:
            return self.config.endpoint
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.config.endpoint}/{path.lstrip('/')}"

    def _headers(self, custom_headers: dict[str, str] | None) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "world-explorer/0.1",
        }
        headers.update(self.authentication_headers())
        headers.update(custom_headers or {})
        return headers

    def authentication_headers(self) -> dict[str, str]:
        """모든 외부 요청에 사용할 인증 헤더를 반환합니다."""
        if not self.config.api_key:
            return {}

        value = self.config.api_key
        if self.config.api_key_prefix:
            value = f"{self.config.api_key_prefix} {value}"
        return {self.config.api_key_header: value}


def load_environment_file(env_file: str | Path | None = None) -> dict[str, str]:
    """.env 값을 읽어 환경변수로 등록하고 읽은 값을 반환합니다."""
    path = Path(env_file) if env_file else Path.cwd() / ".env"
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        normalized_key = key.strip()
        normalized_value = value.strip().strip('"').strip("'")
        values[normalized_key] = normalized_value

    for normalized_key, normalized_value in values.items():
        os.environ.setdefault(normalized_key, normalized_value)
    return values

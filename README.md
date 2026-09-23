# 세상 실험가

일상에서 생기는 모든 “왜?”를 AI와 함께 알아보고 직접 확인해보는 호기심 탐구 앱입니다.

질문하기부터 원리 이해, 관찰, 실험, 기록, 분석까지 한 흐름으로 이어집니다.

## 주요 기능

- 텍스트·음성·사진으로 질문
- 설명 수준 선택
- 꼬리질문 이어가기
- 관찰 계획 생성
- 주변 물건에 맞는 실험 추천
- 실험 단계 안내
- 실험 사진·관찰·측정값 기록
- 실험 결과 분석
- 관련 궁금증 추천
- 궁금증 보관함
- 과학 발견 도감
- 오늘의 궁금증
- 전체 탐험 기록
- Azure OpenAI 연동

## 실행 흐름

```text
궁금증 발견
→ 질문
→ 원리 이해
→ 꼬리질문
→ 직접 관찰·실험
→ 결과 기록
→ 새로운 궁금증 탐험
```

## 기술 구성

- Python
- FastAPI
- Uvicorn
- Azure OpenAI Responses API
- HTML, CSS, JavaScript
- Azure App Service
- Azure Developer CLI
- Bicep

## 로컬 실행

### 1. 가상 환경 활성화

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. 필요한 패키지 설치

```powershell
pip install -r requirements.txt
```

### 3. 환경 설정

프로젝트 루트의 `.env` 파일에 설정을 입력합니다.

```env
WORLD_EXPLORER_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_TIMEOUT_SECONDS=30
```

`.env` 파일은 Git에 올라가지 않도록 제외되어 있습니다.

### 4. 서버 실행

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.world_explorer_vision.main:app --host 127.0.0.1 --port 8000
```

브라우저에서 다음 주소를 엽니다.

- 앱 화면: http://127.0.0.1:8000
- API 문서: http://127.0.0.1:8000/docs
- 상태 확인: http://127.0.0.1:8000/health

## Azure OpenAI 설정

Azure OpenAI를 사용할 때 `.env`의 다음 값을 입력합니다.

```env
WORLD_EXPLORER_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_VERSION=2024-10-21
```

사진 요청은 이미지 데이터를 Base64 형식으로 변환해 Azure OpenAI Responses API의 이미지 입력으로 전달합니다.

API 키는 코드, README, GitHub 저장소에 직접 입력하지 않습니다.

## API 주요 경로

### 질문

- `POST /api/v1/questions/text`
- `POST /api/v1/questions/voice`
- `POST /api/v1/questions/photo`

텍스트 질문 예시:

```json
{
  "questionText": "왜 얼음은 물에 뜰까?",
  "level": "easy"
}
```

### 꼬리질문

- `POST /api/v1/questions/follow-up/start`
- `POST /api/v1/questions/follow-up/{thread_id}`
- `GET /api/v1/questions/follow-up/{thread_id}/history`

### 관찰과 실험

- `POST /api/v1/observation/plan`
- `POST /api/v1/experiments/suggestions`
- `POST /api/v1/experiments/guide/start`
- `POST /api/v1/experiments/guide/{session_id}/step/complete`
- `POST /api/v1/experiments/guide/{session_id}/result/submit`

### 기록과 분석

- `GET /api/v1/vault`
- `GET /api/v1/catalog`
- `GET /api/v1/exploration-record`
- `POST /api/v1/experiments/record/{session_id}/analyze`

### 오늘의 궁금증

- `GET /api/v1/today`
- `POST /api/v1/today/action`

## 데모 실행

전체 기능 흐름은 다음 명령으로 확인할 수 있습니다.

```powershell
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe scripts/demo_question_feature.py
```

## Azure 배포

현재 배포된 앱:

- 앱: https://azappra3c7ywg6n7u2.azurewebsites.net
- API 문서: https://azappra3c7ywg6n7u2.azurewebsites.net/docs
- 상태 확인: https://azappra3c7ywg6n7u2.azurewebsites.net/health

배포 전에는 Azure App Service 설정에 다음 값을 등록해야 합니다.

- `WORLD_EXPLORER_PROVIDER`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_TIMEOUT_SECONDS`

로컬 `.env`는 배포하지 않습니다.

## 프로젝트 구조

```text
.
├── infra/                       # Azure Bicep 인프라
├── scripts/                    # 데모 스크립트
├── src/world_explorer_vision/  # 핵심 서비스와 API
├── web/                        # 앱 화면
├── prd.md                      # 제품 요구사항
├── agent.md                    # AI 행동 지침
├── azure.yaml                 # Azure Developer CLI 설정
└── requirements.txt            # Python 의존성
```

## 보안 주의

- API 키를 GitHub에 올리지 않습니다.
- `.env` 파일을 커밋하지 않습니다.
- API 키가 노출되었다면 Azure Portal에서 즉시 키를 교체합니다.
- 운영 환경에서는 App Service 설정이나 Key Vault를 사용합니다.

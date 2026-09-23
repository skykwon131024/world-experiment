# 세상 실험가

일상에서 생기는 모든 “왜?”를 AI와 함께 알아보고 직접 확인해보는 호기심 탐구 앱입니다.

질문하기부터 원리 이해, 관찰, 실험, 기록, 분석까지 한 흐름으로 이어집니다.

## 앱을 어떻게 사용하는가

세상 실험가는 검색 결과를 보여주는 앱이 아니라, 사용자의 궁금증을 실제 탐구 활동으로 이어주는 앱입니다.

예를 들어 사용자가 `왜 얼음은 물에 뜰까?`라고 질문하면 다음 과정을 진행합니다.

1. 질문의 주제와 대상을 파악합니다.
2. 사용자가 선택한 수준에 맞춰 원리를 설명합니다.
3. `밀도`, `부력`처럼 어려울 수 있는 말을 쉽게 풀이합니다.
4. 이어서 생각해볼 꼬리질문을 추천합니다.
5. 햇빛과 그늘에서 얼음을 비교하는 관찰 방법을 제안합니다.
6. 사용자가 가진 물건으로 할 수 있는 실험을 추천합니다.
7. 실험 단계, 사진, 관찰 메모, 측정값을 기록합니다.
8. 예상 결과와 실제 결과를 비교합니다.
9. 실험에서 확인한 과학 원리를 도감과 보관함에 저장합니다.

이 과정을 통해 사용자는 답을 읽는 데서 끝나지 않고, 직접 확인하고 자신의 탐험 기록을 쌓을 수 있습니다.

## 화면별 설명

### 질문하기 화면

앱의 첫 화면에서 궁금한 점을 입력합니다.

- 질문 문장 입력
- 아주 쉽게, 쉽게, 자세히, 전문적으로 중 설명 수준 선택
- AI 답변 확인
- 관련 주제와 확신도 확인
- 추가 질문 확인
- 관찰 방법과 추천 실험 확인

답변은 긴 원문을 그대로 보여주지 않고 핵심 답변, 자세한 설명, 관찰 방법, 실험 카드로 나누어 보여줍니다.

### 오늘의 궁금증 화면

무엇을 물어볼지 떠오르지 않을 때 사용할 수 있습니다.

- 최근 탐구 기록을 바탕으로 관심 분야를 파악합니다.
- 자연, 생활, 동물, 우주, 과학, 생명, 기술 중 한 분야를 선택합니다.
- 오늘 탐구하기 좋은 질문을 추천합니다.
- `알아보기`를 누르면 설명을 확인합니다.
- `직접 확인하기`를 누르면 관찰 계획과 실험을 확인합니다.

### 궁금증 보관함 화면

지금까지 질문한 내용을 다시 볼 수 있는 공간입니다.

각 항목에는 다음 내용이 저장됩니다.

- 질문 내용
- AI 답변
- 질문 날짜
- 질문 분야
- 관련 사진
- 관련 실험
- 발견한 과학 원리

보관함은 자연, 생활, 동물, 우주, 과학, 생명, 기술로 분류되며, 키워드로 검색할 수 있습니다.

### 과학 발견 도감 화면

탐구하면서 발견한 원리를 분야별로 모아 보여줍니다.

- 물리: 중력, 마찰력, 관성, 공기 저항
- 화학: 용해, 증발, 산화, 산·염기
- 생명과학: 광합성, 세포, 호흡

실험 결과를 분석하면 확인된 과학 원리가 도감에 자동으로 추가됩니다.

### 실험 기록 화면

추천 실험을 단계별로 진행하고 결과를 기록합니다.

1. 실험 재료와 안전 주의를 확인합니다.
2. 첫 번째 단계부터 순서대로 진행합니다.
3. 시작, 중간, 종료 사진을 추가합니다.
4. 관찰한 내용을 메모합니다.
5. 측정값과 단위를 입력합니다.
6. 예상 결과와 실제 결과를 입력합니다.
7. AI 분석 결과를 확인합니다.

### 탐험 기록 화면

사용자가 얼마나 탐구했는지 한눈에 보여줍니다.

- 해결한 궁금증 수
- 완료한 실험 수
- 관찰한 사물 수
- 발견한 과학 원리 수
- 탐험한 분야
- 연속 탐험 일수

## 구체적인 사용 예시

### 예시: 얼음이 물에 뜨는 이유 알아보기

질문:

```text
왜 얼음은 물에 뜰까?
```

앱의 진행:

```text
답변: 얼음은 물보다 밀도가 낮아서 물에 떠요.
꼬리질문: 물이 얼면 왜 밀도가 낮아질까?
관찰: 햇빛과 그늘에서 얼음이 녹는 속도를 비교해보세요.
실험: 얼음 2개를 서로 다른 위치에 놓고 5분 간격으로 기록하세요.
기록: 사진, 관찰 메모, 측정값을 저장하세요.
분석: 햇빛 쪽 얼음이 더 빨리 녹은 이유를 확인하세요.
도감: 열 전달과 밀도에 관련된 원리를 저장하세요.
```

## 입력 방식별 동작

### 텍스트

텍스트 질문은 JSON으로 앱에 전달되고, 답변·관찰 계획·실험 추천이 함께 반환됩니다.

### 음성

음성 인식 결과인 문장을 질문으로 처리합니다. 음성 인식 서비스와 연결하면 사용자가 말한 질문을 바로 탐구할 수 있습니다.

### 사진

사진 파일과 질문을 함께 보내 사물이나 현상을 확인합니다. Azure OpenAI를 사용할 때는 사진이 이미지 입력으로 전달되고, 답변은 텍스트 질문과 같은 앱 형식으로 변환됩니다.

## 앱이 제공하지 않는 것

- 답변만 보여주고 탐구를 끝내지 않습니다.
- 어려운 전문 용어만 나열하지 않습니다.
- 사용자가 하지 않은 실험 결과를 사실처럼 만들지 않습니다.
- 위험한 실험은 추천하지 않습니다.
- API 키를 화면이나 GitHub 저장소에 표시하지 않습니다.

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

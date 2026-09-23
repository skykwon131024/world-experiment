# 6.1 사물·현상 인식 기능 구현 안내

## 구현 범위
이 구현은 PRD의 6.1 기능을 백엔드 API 형태로 동작하도록 만든 최소 실행 버전이다.

포함 기능:
- 사물/현상 후보 인식
- 다중 대상 인식
- 과학 현상 매핑
- 관련 질문 자동 추천
- 재촬영 가능 플래그 제공
- 잘못 인식 수정 저장 API 제공

## 파일 구성
- src/world_explorer_vision/main.py
- src/world_explorer_vision/recognizer.py
- src/world_explorer_vision/knowledge.py
- requirements.txt
- data/recognition_feedback.jsonl (실행 시 자동 생성)

## 실행 방법
1. 의존성 설치
   pip install -r requirements.txt

2. 서버 실행
   uvicorn src.world_explorer_vision.main:app --reload

3. 헬스 체크
   GET /health

## API 1: 인식 요청
경로:
POST /v1/recognize

폼 데이터:
- image: 이미지 파일
- userHint: 선택 입력, 사용자가 추가로 준 힌트 텍스트

동작:
- 파일명 + 힌트에서 대상을 매칭한다.
- 인식 대상별 과학 현상과 추천 질문을 반환한다.
- 인식 결과 수정 가능 여부를 함께 반환한다.

응답 예시:
{
  "target": "사물·현상 인식",
  "result": {
    "requestId": "...",
    "detections": [
      {
        "name": "얼음",
        "confidence": 0.99,
        "phenomena": ["밀도 차이", "상태 변화", "열 전달", "융해"],
        "suggestedQuestions": [
          "왜 얼음은 물에 뜰까요?",
          "왜 얼음은 녹을까요?",
          "얼음은 어떻게 만들어질까요?"
        ]
      }
    ],
    "suggestedQuestions": [
      "왜 얼음은 물에 뜰까요?",
      "왜 얼음은 녹을까요?",
      "얼음은 어떻게 만들어질까요?"
    ],
    "retakeAllowed": true,
    "correctionAllowed": true
  }
}

## API 2: 인식 수정 저장
경로:
POST /v1/recognize/correction

요청 본문(JSON):
- requestId: 인식 요청 ID
- originalName: 기존 인식 이름
- correctedName: 사용자 수정 이름
- note: 선택 입력

동작:
- 수정 이력을 data/recognition_feedback.jsonl에 저장한다.

## 현재 구현의 한계
- 실제 이미지 비전 모델 대신 파일명/힌트 기반 매칭으로 동작한다.
- 고정된 지식 사전 기반이므로 새 사물은 기본 질문으로 처리된다.

## 다음 확장 제안
- 이미지 임베딩 기반 실제 비전 모델 연동
- 인식 후보 Top-K와 바운딩 박스 제공
- 사용자 피드백 기반 자동 재학습 파이프라인
- 설명 수준(아주 쉽게/쉽게/자세히/전문적으로)과 추천 질문 개인화

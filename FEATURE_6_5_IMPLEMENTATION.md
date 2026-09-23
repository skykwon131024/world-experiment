# 6.5 현상 관찰 기능 구현 안내

## 구현 목표
질문에 대한 설명에서 끝나지 않고, 사용자가 직접 확인할 수 있는 관찰 계획을 제공한다.

## 구현 파일
- src/world_explorer_vision/observer.py
- src/world_explorer_vision/knowledge.py (관찰 가이드 데이터)
- src/world_explorer_vision/questioning.py (질문 결과에 관찰 계획 포함)
- scripts/demo_question_feature.py

## 제공 정보
- 무엇을 관찰할지
- 관찰 방법
- 관찰 시간
- 관찰 중 확인할 포인트
- 예상 변화

## 핵심 동작
1. 질문에서 주제를 추정한다.
2. 주제에 맞는 관찰 가이드를 선택한다.
3. 질문 결과 안에 observationPlan을 함께 넣는다.
4. 필요하면 create_observation_plan(question_text)로 관찰 계획만 단독 생성할 수 있다.

## 주요 메서드
- ObservationService.create_plan(topic)
- QuestionService.create_observation_plan(question_text)

## 실행 예시
python scripts/demo_question_feature.py

출력의 OBSERVATION PLAN SAMPLE 블록에서 관찰 계획을 확인할 수 있다.

## 참고
- 현재는 API 없이 코어 로직만 구현했다.
- 이후 API를 붙일 때는 QuestionService의 반환값을 그대로 전달하면 된다.

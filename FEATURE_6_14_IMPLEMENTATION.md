# Feature 6.14 구현 안내

## 구현 목표
사용자의 전체 탐구 활동을 누적 집계해 탐험 기록으로 보여줍니다.

## 반영 파일
- src/world_explorer_vision/exploration_log.py
- src/world_explorer_vision/step_guide.py
- src/world_explorer_vision/questioning.py
- scripts/demo_question_feature.py
- src/world_explorer_vision/__init__.py

## 구현 내용
1. 탐험 기록 집계 서비스 추가
- ExplorationLogService
- 입력 데이터: 궁금증 보관함, 실험 세션, 과학 도감

2. 기록 항목 집계
- 해결한 궁금증 수: 보관함 항목 수
- 직접 수행한 실험 수: 상태 completed인 실험 세션 수
- 관찰한 사물 수: 보관함 topic(일반 제외) 고유 개수
- 발견한 과학 원리 수: 도감 discoveredPrinciples 고유 개수
- 탐험한 분야: 보관함 category 고유 목록
- 연속 탐험 기록: 질문 날짜 기준 최장 연속 일수

3. 요약 문구 생성
- 궁금증 해결 N개
- 실험 완료 N회
- 발견한 원리 N개
- 새로운 질문 N개

4. 질문 서비스 연동
- get_exploration_record() 메서드로 통합 결과 반환

## 반환 예시 키
- solvedCuriosityCount
- completedExperimentCount
- observedObjectCount
- discoveredPrincipleCount
- exploredCategories
- consecutiveExplorationDays
- summary

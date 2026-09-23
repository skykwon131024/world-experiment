# Feature 6.13 구현 안내

## 구현 목표
사용자가 질문 주제를 떠올리기 어려울 때 오늘의 궁금증을 추천하고,
선택한 행동(알아보기/직접 확인하기)으로 바로 탐구를 이어가게 합니다.

## 반영 파일
- src/world_explorer_vision/today_curiosity.py
- src/world_explorer_vision/questioning.py
- scripts/demo_question_feature.py
- src/world_explorer_vision/__init__.py

## 구현 내용
1. 오늘의 궁금증 추천
- get_today_curiosity(limit=1)
- 추천 질문, 추천 분야, 추천 이유, 행동 선택지를 반환

2. 과거 기록 반영
- 궁금증 보관함 기록(category, topic)을 점수화해 관심 분야를 계산
- 관심 분야 질문 은행에서 질문을 추천

3. 행동 선택
- 알아보기: choose_today_curiosity_action(question, "알아보기")
  - 일반 질문 흐름으로 설명/관찰/실험 추천 반환
- 직접 확인하기: choose_today_curiosity_action(question, "직접 확인하기")
  - 관찰 계획 + 실험 추천을 즉시 반환

4. 기본 선택지
- 알아보기
- 직접 확인하기

## 반환 예시 키
- get_today_curiosity
  - count
  - items[]
    - question
    - category
    - basedOnHistory
    - reason
    - availableActions
- choose_today_curiosity_action
  - action
  - mode
  - result 또는 observationPlan/experimentSuggestions

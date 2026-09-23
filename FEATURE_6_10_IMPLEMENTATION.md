# 6.10 관련 궁금증 추천 기능 구현 안내

## 구현 목표
하나의 질문을 해결하면 관련된 다음 질문을 자동으로 추천한다.

## 구현 파일
- src/world_explorer_vision/recommender.py
- src/world_explorer_vision/knowledge.py (주제별 관련 질문 그래프)
- src/world_explorer_vision/questioning.py
- scripts/demo_question_feature.py

## 핵심 동작
1. 현재 질문에서 주제를 추정한다.
2. 주제에 맞는 관련 질문 목록을 불러온다.
3. 현재 질문과 같은 문장은 제외한다.
4. 다음 탐구용 질문 4개를 추천한다.

## 주요 메서드
- QuestionService.recommend_related_questions(current_question, limit=4)

## 반환 데이터
- topic
- currentQuestion
- relatedQuestions

## 실행 예시
python scripts/demo_question_feature.py

출력의 RELATED QUESTION SAMPLE 블록에서 추천 결과를 확인할 수 있다.

# 6.6 실험 추천·생성 기능 구현 안내

## 구현 목표
질문 주제와 주변 물건을 바탕으로 직접 해볼 수 있는 실험을 추천한다.

## 구현 파일
- src/world_explorer_vision/experimenter.py
- src/world_explorer_vision/knowledge.py (실험 템플릿 데이터)
- src/world_explorer_vision/questioning.py (질문 결과에 실험 추천 포함)
- scripts/demo_question_feature.py

## 제공 정보
- 실험 제목
- 실험 목적
- 준비물
- 실험 방법
- 예상 결과
- 소요 시간
- 난이도
- 안전 주의사항
- 추천 이유

## 핵심 동작
1. 질문에서 주제를 추정한다.
2. 주제에 맞는 실험 템플릿을 선택한다.
3. 사용자가 가진 물건과 필요 물건을 비교한다.
4. 바로 가능한 실험을 우선 노출한다.
5. 부족한 준비물이 있으면 추천 이유에 알려준다.

## 주요 메서드
- ExperimentService.suggest(topic, available_items, limit)
- QuestionService.create_experiment_suggestions(question_text, available_items)

## 실행 예시
python scripts/demo_question_feature.py

출력의 EXPERIMENT SUGGESTION SAMPLE 블록에서 결과를 확인할 수 있다.

## 참고
- API 없이 코어 로직만 구현했다.
- 이후 API를 붙일 때는 QuestionService 결과를 그대로 전달하면 된다.

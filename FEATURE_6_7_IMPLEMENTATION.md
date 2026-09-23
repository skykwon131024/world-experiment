# 6.7 실험 단계 안내 기능 구현 안내

## 구현 목표
실험을 한 번에 길게 보여주지 않고 단계별로 진행한다.
현재 단계를 완료해야 다음 단계로 넘어간다.

## 구현 파일
- src/world_explorer_vision/step_guide.py
- src/world_explorer_vision/questioning.py
- scripts/demo_question_feature.py

## 핵심 동작
1. 추천된 실험으로 세션을 시작한다.
2. 현재 단계만 활성 상태로 유지한다.
3. 완료 처리 전에는 다음 단계로 넘어가지 않는다.
4. 마지막 단계 완료 후 결과 입력 대기 상태로 전환한다.
5. 결과 입력 제출 후 세션 완료로 종료한다.

## 주요 메서드
- QuestionService.start_experiment_guide(question_text, available_items=None, selected_index=0)
- QuestionService.complete_experiment_step(session_id)
- QuestionService.get_experiment_guide(session_id)
- QuestionService.submit_experiment_result(session_id)

## 상태 값
- in_progress: 단계 진행 중
- awaiting_result: 단계 완료, 결과 입력 대기
- completed: 결과 입력까지 완료

## 실행 예시
python scripts/demo_question_feature.py

출력의 STEP GUIDE SAMPLE 블록에서 단계 진행 흐름을 확인할 수 있다.

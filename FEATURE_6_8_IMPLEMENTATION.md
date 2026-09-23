# 6.8 실험 과정 기록 기능 구현 안내

## 구현 목표
실험 과정을 사진과 글로 저장하고, 나중에 다시 확인할 수 있게 한다.

## 구현 파일
- src/world_explorer_vision/recorder.py
- src/world_explorer_vision/questioning.py
- scripts/demo_question_feature.py

## 저장 항목
- 실험 시작 사진
- 실험 중간 사진
- 실험 종료 사진
- 관찰 내용
- 측정값
- 예상 결과
- 실제 결과

## 핵심 동작
1. 실험 단계 세션 시작 시 기록 세션도 함께 시작한다.
2. 단계별 사진을 start/middle/end로 나눠 저장한다.
3. 관찰 메모를 여러 개 누적 저장한다.
4. 측정값 이름/값/단위를 누적 저장한다.
5. 예상 결과와 실제 결과를 각각 저장한다.
6. 현재 기록 상태를 언제든 조회할 수 있다.

## 주요 메서드
- QuestionService.add_experiment_photo(session_id, stage, photo_ref)
- QuestionService.add_experiment_observation(session_id, note)
- QuestionService.add_experiment_measurement(session_id, name, value, unit)
- QuestionService.set_experiment_expected_result(session_id, text)
- QuestionService.set_experiment_actual_result(session_id, text)
- QuestionService.get_experiment_record(session_id)

## 실행 예시
python scripts/demo_question_feature.py

출력의 EXPERIMENT RECORD SAMPLE 블록에서 기록이 누적되는 모습을 확인할 수 있다.

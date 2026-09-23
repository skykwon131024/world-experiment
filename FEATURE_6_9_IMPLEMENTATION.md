# 6.9 실험 결과 분석 기능 구현 안내

## 구현 목표
기록된 예상 결과와 실제 결과를 비교해 원인과 의미를 설명하고, 다음 실험까지 추천한다.

## 구현 파일
- src/world_explorer_vision/analyzer.py
- src/world_explorer_vision/questioning.py
- scripts/demo_question_feature.py

## 분석 항목
- 예상 결과와 실제 결과 비교
- 결과 일치 여부 판단
- 결과 차이 원인 추정
- 관련 과학 원리 설명
- 실험 과정 오차 가능성 안내
- 추가 실험 추천

## 핵심 동작
1. 기록 세션에서 예상/실제 결과를 읽는다.
2. 문장 유사도와 핵심 단어를 기준으로 일치 여부를 판단한다.
3. 주제별 가능한 원인 목록과 관찰 메모를 함께 반영해 원인을 추정한다.
4. 사진/측정/메모의 기록 상태를 점검해 오차 가능성을 안내한다.
5. 다음에 시도할 실험 1~2개를 추천한다.

## 주요 메서드
- QuestionService.analyze_experiment_result(session_id, topic=None)

## 반환 데이터
- topic
- expectedResult
- actualResult
- matchStatus (matched, mismatched, insufficient)
- comparisonSummary
- likelyCauses
- sciencePrinciple
- possibleErrors
- nextExperiments

## 실행 예시
python scripts/demo_question_feature.py

출력의 EXPERIMENT ANALYSIS SAMPLE 블록에서 분석 결과를 확인할 수 있다.

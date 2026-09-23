# 6.4 꼬리질문 기능 구현 안내

## 구현 목표
같은 주제의 질문을 연속으로 이어가고, 이전 맥락을 유지해 대화가 끊기지 않게 한다.

## 구현 파일
- src/world_explorer_vision/questioning.py
- scripts/demo_question_feature.py

## 제공 메서드
1. start_follow_up(first_question, level="easy")
- 새 대화 스레드를 만든다.
- 첫 질문과 AI 답변을 기록한다.
- 다음에 물어볼 질문 후보를 함께 반환한다.

2. ask_follow_up(thread_id, question_text, level="easy")
- 기존 스레드 맥락으로 꼬리질문을 처리한다.
- 이전 주제를 유지하거나 새 질문에서 주제가 잡히면 갱신한다.
- 질문/답변 기록 수를 누적한다.

3. get_follow_up_history(thread_id)
- 해당 스레드의 누적 대화 기록을 반환한다.

## 반환 데이터
- threadId: 대화 스레드 ID
- turnIndex: 몇 번째 질문인지
- question: 현재 질문
- answer: 현재 답변
- topic: 현재 주제
- selectedLevel: 선택된 설명 수준
- suggestedNextQuestions: 다음 질문 추천 목록
- historyCount: 누적 대화 턴 수

## 핵심 동작
- AI는 threadId 기준으로 이전 질문/답변을 기억한다.
- 질문이 이어질수록 같은 주제를 단계적으로 깊게 탐구할 수 있다.
- 매 턴마다 다음에 물어볼 질문 버튼 후보를 추천한다.

## 실행 예시
python scripts/demo_question_feature.py

출력의 FOLLOW-UP SAMPLE, FOLLOW-UP HISTORY 블록에서 꼬리질문 흐름을 확인할 수 있다.

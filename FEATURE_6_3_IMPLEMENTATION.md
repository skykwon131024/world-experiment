# 6.3 맞춤형 설명 기능 구현 안내

## 구현 목표
같은 질문이라도 설명 수준을 바꿔 답변하고, 어려운 용어는 바로 풀이를 보여준다.

## 구현 파일
- src/world_explorer_vision/explainer.py
- src/world_explorer_vision/knowledge.py (설명 데이터/용어 사전)
- src/world_explorer_vision/questioning.py (질문 결과에 설명 포함)

## 지원 설명 수준
- very_easy (아주 쉽게)
- easy (쉽게)
- detailed (자세히)
- professional (전문적으로)

## 동작 방식
1. 질문에서 주제를 추정한다.
2. 선택한 설명 수준에 맞는 문장을 고른다.
3. 설명 문장 안의 어려운 용어를 찾아 풀이를 붙인다.
4. 결과에 현재 수준, 다른 선택 가능 수준, 용어 풀이 목록을 함께 넣는다.

## 핵심 반환 필드
questioning 결과 안에 explanation이 추가된다.
- selectedLevel: 현재 설명 수준
- explanation: 수준에 맞는 설명 문장
- availableLevels: 선택 가능한 수준 목록
- termHelp: 어려운 용어와 쉬운 뜻 목록

## 실행 예시
python scripts/demo_question_feature.py

출력 JSON에서 explanation 항목을 확인하면 수준별 설명과 용어 풀이가 함께 나온다.

## API 연결 전제
- 현재는 API 없이 코어 로직만 구현했다.
- 나중에 API를 붙일 때 QuestionService의 level 파라미터를 그대로 받으면 된다.

# 6.2 궁금증 질문 기능 구현 안내

## 구현 목표
API 없이도 텍스트, 음성, 사진 질문을 같은 처리 흐름으로 분석하고 결과를 반환한다.

## 구현 파일
- src/world_explorer_vision/questioning.py
- scripts/demo_question_feature.py

## 핵심 동작
1. 텍스트 질문
- ask_text(question_text)
- 질문 문장을 정리하고 주제를 추정한다.

2. 음성 질문
- ask_voice(transcript)
- 음성 인식 결과 텍스트를 텍스트 질문과 같은 방식으로 처리한다.

3. 사진 질문
- ask_photo(image_file_name, question_text=None, image_hint=None)
- 이미지 파일명과 힌트로 대상을 먼저 추정한다.
- 질문이 없으면 자동 추천 질문을 기본 질문으로 사용한다.

## 반환 데이터
- source: text, voice, photo
- normalizedQuestion: 정리된 질문 문장
- interpretedTopic: 추정한 주제
- confidence: 주제 추정 신뢰도
- answerPreview: 쉬운 설명 미리보기
- suggestedQuestions: 관련 질문 추천 목록

## 실행 예시
python scripts/demo_question_feature.py

실행하면 텍스트, 음성, 사진 질문 샘플 결과가 JSON으로 출력된다.

## 주의
- 이 구현은 API 라우트 없이 코어 로직만 만든 상태다.
- 이후 API가 필요하면 이 서비스 클래스를 그대로 호출하도록 붙이면 된다.

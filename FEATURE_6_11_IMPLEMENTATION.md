# Feature 6.11 구현 안내

## 구현 목표
궁금증 보관함 기능을 구현해 사용자의 질문 흐름을 자동으로 저장하고,
분류 변경과 검색까지 가능하도록 합니다.

## 반영 파일
- src/world_explorer_vision/vault.py
- src/world_explorer_vision/questioning.py
- scripts/demo_question_feature.py
- src/world_explorer_vision/__init__.py

## 구현 내용
1. 자동 저장
- 텍스트/음성/사진 질문 응답 시 보관함에 자동 저장됩니다.
- 꼬리질문도 자동 저장됩니다.

2. 저장 정보
- 질문 내용
- AI 답변
- 질문 날짜(UTC ISO 문자열)
- 관련 사진
- 관련 실험
- 발견한 과학 원리
- 분류

3. 분류
- 기본 분류 목록: 자연, 생활, 동물, 우주, 과학, 생명, 기술
- 질문/주제 기반 자동 분류

4. 사용자 제어
- 분류 변경: update_curiosity_category(entry_id, new_category)
- 검색: search_curiosity_vault(keyword)
- 목록 조회: get_curiosity_vault(category=None, keyword=None)

5. 실험 연결
- 실험 가이드 시작 시 최근 같은 주제 항목에 실험 세션 ID 연결
- 실험 분석 완료 시 최근 같은 주제 항목에 과학 원리 추가

## 반환 예시 키
- get_curiosity_vault
  - count
  - entries[]
- update_curiosity_category
  - entryId, category 등 항목 전체
- search_curiosity_vault
  - keyword, count, entries[]

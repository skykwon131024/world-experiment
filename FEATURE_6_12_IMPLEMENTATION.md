# Feature 6.12 구현 안내

## 구현 목표
탐구 과정에서 발견한 과학 원리를 분야별 도감으로 자동 정리합니다.

## 반영 파일
- src/world_explorer_vision/catalog.py
- src/world_explorer_vision/questioning.py
- scripts/demo_question_feature.py
- src/world_explorer_vision/__init__.py

## 구현 내용
1. 도감 기본 분야 구성
- 물리: 중력, 마찰력, 관성, 공기 저항
- 화학: 용해, 증발, 산화, 산·염기
- 생명과학: 광합성, 세포, 호흡

2. 자동 추가
- 실험 분석 완료 시 sciencePrinciple 값을 자동으로 도감에 추가
- 중복 원리는 다시 추가하지 않음

3. 분야 분류
- 주제와 원리 키워드 기반으로 물리/화학/생명과학 자동 분류

4. 조회/검색
- 전체/분야별 조회: get_science_catalog(field_name=None)
- 키워드 검색: search_science_catalog(keyword)

## 반환 예시 키
- get_science_catalog
  - count
  - catalog[]
    - fieldName
    - baselinePrinciples[]
    - discoveredPrinciples[]
- search_science_catalog
  - keyword
  - count
  - results[]

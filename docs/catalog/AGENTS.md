# 기술·스킬 카탈로그 작업 가이드

## 1. WHAT — 역할
도메인·작업 목적·제품에서 agent/도구/스킬을 찾는다. 원문 이름과 설치 이름을 구분한다.

## 2. CONTENTS — 파일과 기술
- README.md — 검색 진입
- contracts.md, contracts/ — research-v1과 다른 9개 조합의 mission-v1 schema·공급자 형식·fixture 연결
- agent-types.md, agents-index.json — 9개 형태
- tools.md, tools/, tools-index.json — 도구 카드
- tools/openshell-security.md — 버전별 실행 경계·정책 조사; 제품 적용은 ../product/agent-design.md
- skills-index.json — 전체 metadata 원본
- skills/ — 자동 생성 도메인/작업 뷰
- recipes-index.json — 미션 레시피 검색 metadata

기술: Markdown/JSON 중심; scripts는 Python/Bash, design은 HTML/CSS/JavaScript.

## 3. HOW — 수정 방법
기술 변경은 공식 source/revision을 확인한다. 원본 metadata는 refresh_catalog.py, 분류/뷰는 classify_skills.py로 생성한다. 파일 수/분류/참조를 validate.py로 확인한다.

## 4. HOW NOT — 주의할 함정
- 생성된 skills/ leaf를 직접 고치지 않는다 — 재생성에서 유실된다.
- 전체 인덱스를 context에 통째로 넣지 않는다 — 필요한 원문보다 잡음이 커진다.
- 스킬 metadata 수집을 제품 실행 성공으로 기록하지 않는다 — 키/GPU/입력 검증이 별도다.

## 5. WHERE — 의존성과 경계
lookup.py와 playbooks가 소비한다. 공식 categories와 프로젝트 domains/functions를 구분한다.

## 6. WHY — 배경
범위를 고정한 전체 인덱스로 탐색 누락을 줄이고 필요한 소수의 원문만 읽는다.
알려진 사실/기존 결정만 기재했다. 추가 도메인 고유 함정은 사용자 확인 후 보완한다.

## 7. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
명시한 `$learn`/`/learn`에서만 추가한다.

_(아직 없음)_

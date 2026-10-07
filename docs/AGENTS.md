# 문서 전체 작업 가이드

## 1. WHAT — 역할
공식 자료와 팀 실행 지침을 분리한 문서 지도. 새 미션의 조합과 실행법을 찾는 진입점이다.

## 2. CONTENTS — 파일과 기술
- intent/INTENT.md — 사용자 문제·목적·기능 방향
- PRD.md / ARCHITECTURE.md / ADR.md — 요구사항 / 구조 / 결정 이유의 원본
- plan.md — 단계별 구현 순서·의존성·완료 조건; 개인 HANDOFF와 구분
- product/ — 제품 문서 진입·데이터 근거
- catalog/ — 기술/스킬 원본과 탐색 뷰
- playbooks/ — 조합·quickstart
- evaluation/ — 주제 선정 기준·구현 평가·예선 근거
- operations/ — 행사·운영
- design/ — 디자인 문서

기술: Markdown/JSON 중심; scripts는 Python/Bash, design은 HTML/CSS/JavaScript.

## 3. HOW — 수정 방법
하위 영역 가이드를 읽고 변경한다. 원본 정보는 한 곳에서 관리하고 상대 링크를 갱신한다. 완료 보고·작업 이력 문서는 만들지 않고 실제 사용에 필요한 내용만 유지한다.

## 4. HOW NOT — 주의할 함정
- 공식 배점을 내부 제안으로 추정해 확정하지 않는다 — 실제 규정과 채점 목적이 다르다.

## 5. WHERE — 의존성과 경계
INTENT는 목적·방향, PRD는 요구사항, ARCHITECTURE는 구조, ADR은 결정 이유의 원본이다. product/는 이 문서들의 진입과 데이터 근거를 관리하며 operations의 공식 요건과 catalog/playbooks/evaluation의 준비 자료를 참조한다. evaluation의 주제 선정 기준 → catalog와 playbooks의 조합·실행 → evaluation의 구현 평가 순서로 사용한다. 선정과 구현 평가의 점수·목적은 구분한다.

## 6. WHY — 배경
당일 7시간이므로 모든 문서를 읽지 않고 필요한 경로만 따라가는 구조를 사용한다.
알려진 사실/기존 결정만 기재했다. 추가 도메인 고유 함정은 사용자 확인 후 보완한다.

## 7. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
명시한 `$learn`/`/learn`에서만 추가한다.

_(아직 없음)_

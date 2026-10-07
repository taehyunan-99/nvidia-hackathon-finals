# 제품 정의 작업 가이드

## 1. WHAT — 역할
사용자가 선택한 한국 가족 문화체험 MVP와 선택 기능의 경계를 관리한다. 구현 전 계약·데이터 근거를 구체화하며 실행 여부를 구분한다.

## 2. CONTENTS — 파일과 기술
- README.md — INTENT·PRD·ARCHITECTURE·ADR의 원본 역할과 진입
- agent-design.md — ARCHITECTURE·PRD와 기존 실행 자료의 연결
- data-sources.md — 공식 데이터·확인한 사례·접근 한계

기술: Markdown 설계 문서. 앱 스택은 ADR-008의 React·TypeScript·Vite와 Python·FastAPI·Pydantic, 에이전트 조합은 ADR-012의 단일 NAT ReAct·hosted Nemotron/NIM을 기준으로 한다. 최종 제품 schema·모델 ID·실제 통합은 미확정·미검증이다.

## 3. HOW — 수정 방법
사용자 결정은 목적·방향이면 ../intent/INTENT.md, 요구사항이면 ../PRD.md, 구조면 ../ARCHITECTURE.md, 선택 이유면 ../ADR.md에 반영하고 데이터 근거와 대조한다. 후보·제안·미검증을 확정 기능이나 실행 성공으로 바꾸지 않는다. `python3 scripts/validate.py`로 링크·가이드 참조를 확인한다.

## 4. HOW NOT — 주의할 함정
- GPS·지도·이동·영어·통역 검색을 기본 MVP로 되돌리지 않는다 — 사용자가 작업 중 채택/제외할 서브미션으로 분리했다.
- 단순 필터·고정 도구 순서를 에이전트 판단으로 표현하지 않는다 — 추가 확인과 대안 선택의 이득을 검증해야 한다.

## 5. WHERE — 의존성과 경계
공식 요건은 ../operations/mission.md, 도구 원본은 ../catalog/, 실행 절차는 ../playbooks/, 평가 기준은 ../evaluation/, 디자인은 ../design/을 따른다. 제품 원본은 README가 연결하는 네 문서이며 이 폴더와 일반 가이드에 전체 요구사항을 복제하지 않는다.

## 6. WHY — 배경
2026-10-07 인터뷰로 관심 분야에서 가족 체험을 발견하고 후보를 비교·선택하는 과업을 확정했다. 참여조건 확인은 추천 신뢰성을 뒷받침하고 지도·영어 등은 선택 기능이다. 한정된 본선 시간에 핵심 과업의 완주를 먼저 검증한다.

## 7. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
명시한 `$learn`/`/learn`에서만 추가한다.

_(아직 없음)_

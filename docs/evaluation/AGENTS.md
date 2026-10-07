# 평가·프로젝트 분석 작업 가이드

## 1. WHAT — 역할
<!-- prev: 내부 점수와 Bio-3 관찰 증거 중심 → 2026-10-05 사용자 승인으로 주제 선정과 구현 평가를 구분하고 분석·실행 근거의 역할을 분리. -->
주제 선정 기준과 구현 평가를 분리해 관리한다. Bio-3의 선정 분석·실행 근거는 별도 문서에 두고 공식 심사 원인과 내부 추정을 구분한다.

## 2. CONTENTS — 파일과 기술
- README.md — 주제 선정 → 조합·실행 → 구현 평가 진입
- agent-rubric.md/json, frontend-rubric.md/json — 현재 영역별 항목/가중치
- integration.md/json — 공동 통합 관문
- legacy/ — 이전 루브릭·채점법·재계산용 양식
- ../../.agents/skills/agent-rubric/, frontend-rubric/ — 영역별 근거 기반 평가
- scoring-guide.md — 관찰 증거·채점·개선 우선순위
- bio3-review.md — 예선 구현·실행 기록과 해석 한계
- topic-analysis.md — 선정 경위·적합성·장단점과 근거
- topic-selection.md — 주제 선정 항목·배점·관문·반례의 해석 원본
- topic-rubric.json, templates/topic-scorecard.json — topic-v1 계산 기준·양식
- ../../.agents/skills/topic-rubric/ — 주제 선정 평가 스킬
- rubric-research.md — 구현 평가의 조사 근거와 설계 이유
- templates/ — 빈/예시 채점표·사례

기술: Markdown/JSON 중심; scripts는 Python/Bash, design은 HTML/CSS/JavaScript.

## 3. HOW — 수정 방법
배점 변경 시 rubric version을 바꾸고 score.py/test_score.py 호환성을 확인한다. 실행 모드와 코드 버전을 함께 기록한다.
주제 선정 항목·판정식은 topic-selection.md에서 관리하고 playbooks에는 링크로 연결한다. topic-v1의 JSON 계산 기준과 문서의 항목·등급·관문을 함께 갱신한다.
문서 변경은 `python3 scripts/validate.py`로 확인하고, 기존 채점 로직 변경 시 `python3 -m unittest discover -s scripts -p 'test_score*.py'`를 실행한다.

## 4. HOW NOT — 주의할 함정
- 과거 13/20 또는 6/6을 현재 본선 성능으로 바꾸지 않는다 — 코드/입력/환경이 다르다.
- 실행 실패를 분모에서 빼지 않는다 — 가용성을 숨긴다.

## 5. WHERE — 의존성과 경계
현재 평가 대상·MVP 경계는 ../product/README.md, 입력 자료와 미확인은 ../product/data-sources.md에서 가져온다. playbooks는 topic-selection.md의 선정 기준을 참조하고, 실행 결과를 구현 평가의 근거로 제공한다. scripts/score.py는 주제 선정·구현·통합·legacy JSON을 구분해 읽는다.

## 6. WHY — 배경
본선 진출의 정확한 심사평은 없다. 자료 기반 잠정 평가는 개발 우선순위를 위한 도구다.
알려진 사실/기존 결정만 기재했다. 추가 도메인 고유 함정은 사용자 확인 후 보완한다.

## 7. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
명시한 `$learn`/`/learn`에서만 추가한다.

_(아직 없음)_

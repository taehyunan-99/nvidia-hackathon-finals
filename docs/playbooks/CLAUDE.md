# 조합·사용법 작업 가이드

## 1. WHAT — 역할
미션에서 조합을 고른 뒤 설치→실행→검증으로 연결하는 절차.

## 2. CONTENTS — 파일과 기술
- agent-flow.md — 목표·상태·도구 선택·검증·종료의 공통 흐름
- model-policy.md, model-policy.json — 본선 공통 모델 호출 기본값·적용 경계
- rehearsal.md, examples/research/ — 오프라인 계약 리허설과 합성 fixture
- README.md, missions/ — 미션별 조합
- quickstarts/ — 실제 시작 절차
- skill-setup.md — 최신/고정 스킬 확보
- examples/nat/ — 구성 예제
- recipes.md — 선정된 주제의 도구 조합·최소 실행·축소 경로
- harness.md, templates/mission.md — 실행 구조·미션 입력 계약

기술: Markdown/JSON 중심; scripts는 Python/Bash, design은 HTML/CSS/JavaScript.

## 3. HOW — 수정 방법
대상 도구의 catalog 카드와 버전별 원문을 확인한 뒤 명령을 기록한다. 입력·출력·실패·성공 기준·검증 상태를 함께 갱신한다.
후보 비교는 ../evaluation/topic-selection.md를 참조하고 recipes.md에는 조합·실행 안내만 둔다. 문서 링크는 `python3 scripts/validate.py`로 확인한다.

## 4. HOW NOT — 주의할 함정
- 포트/model ID/payload를 추측해 실행 지침으로 확정하지 않는다 — 버전·계정별 지원이 다르다.
- 전문 GPU stack을 모두 기본 설치하지 않는다 — 7시간 내 핵심 경로 검증이 우선이다.

## 5. WHERE — 의존성과 경계
evaluation의 주제 선정 기준을 받아 catalog의 도구·agent 형태로 실행 조합을 만든다. 실행 후 evaluation의 구현 평가 양식에 근거를 연결한다.

## 6. WHY — 배경
설명만 있는 링크 목록에서 실제 첫 행동까지 시간을 줄이는 것이 목적이다.
알려진 사실/기존 결정만 기재했다. 추가 도메인 고유 함정은 사용자 확인 후 보완한다.

## 7. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
명시한 `$learn`/`/learn`에서만 추가한다.

_(아직 없음)_

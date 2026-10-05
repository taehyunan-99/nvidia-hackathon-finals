---
name: agent-rubric
description: Evaluate this hackathon project's agent with the approved finals-v1 100-point rubric using implementation and run evidence; report scores, unknowns, blocking gates, and concrete improvements. Use for agent readiness or rubric assessment, not guide quality, HER2-only evaluation, or schedule planning.
---

# Agent Rubric

이 저장소의 승인된 평가 기준을 반복 적용한다. 모델의 실제 판단·도구 실행과 코드/규칙의 검증을 구분한다. 배점·등급 기준을 임의로 바꾸지 않는다.

## 필요한 자료만 읽기

- 평가 대상: [에이전트 흐름](../../../docs/playbooks/agent-flow.md).
- 기준 원본: [rubric.md](../../../docs/evaluation/rubric.md)와 [rubric.json](../../../docs/evaluation/rubric.json).
- 해석·우선순위: [채점 방법](../../../docs/evaluation/scoring-guide.md).
- 빈 기록: [scorecard.json](../../../docs/evaluation/templates/scorecard.json).
- 집계: [scripts/score.py](../../../scripts/score.py).

다른 프로젝트를 평가해도 위 기준을 쓰되 대상 경로/commit/실행 환경을 구분한다. 이 스킬만 단독 복사하면 의존 문서/채점기가 없으므로 참조를 함께 준비해야 한다.

## 평가 절차

1. 현재 대상과 범위를 기록한다. HEAD가 없으면 working tree와 핵심 파일 hash를 쓰고 commit을 만들지 않는다. 요청이 설계 검토라면 설계 근거로만 평가한다.
2. 모델이 선택한 행동, 실제 도구 반환값, validator 결과, 최종 산출물의 연결을 확인한다. 코드 존재/과거 기록/현재 실행을 별도로 표시한다.
3. 8개 항목을 원본의 0–4등급 또는 null로 채운다. pass/fail 점수에는 실제 확인한 파일/명령/출력 위치와 짧은 이유를 붙인다. 기록이 없거나 실행하지 못한 항목은 추정으로 채우지 않는다.
4. 미션 규정·live 경로·근거 무결성·실패 처리·제출 관문을 pass/fail/unknown으로 따로 판정한다. 높은 총점이 관문 실패를 상쇄하지 않는다.
5. 평가 기록이 요청 범위에 포함되면 `docs/evaluation/reviews/`의 새 평가명 폴더에 입력 채점표와 보고를 저장한다. 같은 평가 파일을 덮어쓰지 않는다. 간단한 의견 요청이면 채팅으로만 보고해도 된다.
6. 저장한 채점표를 저장소 루트의 `python3 scripts/score.py 채점표경로`로 집계한다. 사람이 매긴 등급/근거의 진위까지 집계기가 보증하는 것은 아니다.

## 결과 형식

- 대상/기준 버전/평가 모드, 총점과 미채점 가중치.
- 항목별 등급·가중 점수·근거·한계.
- 실패/미확인 관문과 이를 해소할 다음 행동.
- 가장 효과적인 개선 최대 3개. 무엇을 관찰하면 개선됐다고 인정할지 포함.

승인된 스케줄은 없으므로 시각·일정·개발 시간표를 만들지 않는다. 설치/스킬 제작 요청을 실제 프로젝트 평가 실행으로 해석하지 않는다.

## 해석 경계

- 내부 80점 목표는 대회 통과선/입상 확률이 아니다.
- mock/replay 성공, HTTP 200, 테스트 개수를 live agent 품질로 바꾸지 않는다.
- 근거 부족에 모두 보류하는 구현은 결과 정확성 만점의 근거가 아니다.
- 실제 API·GPU 시험이 필요하면 계정/범위/예산이 확보된 요청에만 수행한다. 자료 검토만으로 모델을 호출하지 않는다.
- 평가 요청은 제품 수정·추가 스킬 실행·commit/push를 포함하지 않는다.

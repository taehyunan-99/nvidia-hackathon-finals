---
name: agent-rubric
description: Evaluate agent decisions, tool use, verified outcomes and bounded execution with agent-v2; exclude frontend appearance and presentation scoring.
---

# 에이전트 루브릭

에이전트 영역만 근거로 평가하고 구체적인 다음 검증을 제시한다. 이 스킬을 만드는 요청은 실제 제품 채점 요청이 아니다. 평가 요청은 구현 수정·추가 API/GPU 호출·commit/push를 승인하지 않는다.

## 필요한 자료

- [영역 기준](../../../docs/evaluation/agent-rubric.md)과 [등급·배점 원본](../../../docs/evaluation/agent-rubric.json).
- [공통 채점 방법](../../../docs/evaluation/scoring-guide.md), [채점표](../../../docs/evaluation/templates/agent-scorecard.json), [채점기](../../../scripts/score.py).
- 평가 원칙의 근거가 필요할 때만 [조사 자료](../../../docs/evaluation/rubric-research.md).
- 전체 서비스 통합까지 요청한 경우에만 [통합 관문](../../../docs/evaluation/integration.md)과 상대 영역 채점표를 읽는다.

다른 프로젝트를 대상으로 하더라도 subject/revision/environment와 실제 근거를 그 대상에 맞춘다. 스킬만 단독 복사하면 기준·채점기가 없으므로 위 의존 파일을 함께 준비한다.

## 적용

1. 평가 대상·코드와 변경 파일 hash·환경·design/mock/replay/live/mixed 모드·사전 완료 조건을 확인한다. 확보하지 못한 항목은 null/unknown으로 남긴다. 대상·코드 버전·환경 식별 자체가 없으면 숫자 집계를 보류하고 확보한 관측과 필요한 식별 자료만 보고한다.
2. 모델의 선택·실제 도구 반환·독립 검증·종료 제어를 추적한다. 정상/관측 변화/부족/실패/권한 경계의 사례와 같은 예산의 단순 기준선을 확인한다. 장식적 NVIDIA 사용이나 스킬 수로 점수를 올리지 않는다.
3. 7개 항목에 0~4 또는 null, evidence_level·항목별 evidence_mode, 근거 위치, 기대→관측→판정 이유를 기록한다. 모든 하위 조건이 충족된 등급만 준다. 상한·최저 등급·필수 관문은 공통 방법을 따른다. 테스트 개수나 자기 확신으로 등급을 올리지 않는다.
4. `python3 scripts/score.py 채점표.json`으로 집계한다. 계산 입력은 /tmp에 둘 수 있다. 저장소 평가 보고서는 명시 요청이 있을 때만 저장한다. 근거 문자열의 진위는 직접 확인하며 채점기가 검증했다고 표현하지 않는다.
5. 대상/버전/모드, 영역 점수·미채점·최저 등급 미달, 항목별 근거와 관문, 개선 최대 3개와 재검증 조건을 보고한다. 전체 서비스 준비 완료와 구분한다.

공통 통합을 요청받으면 동일 대상/버전/환경의 두 영역 채점표와 integration-scorecard를 연결해 같은 채점기로 검증한다. 두 100점을 합산/평균하지 않는다. 상대 영역 근거가 없으면 통합은 미확인이다. 발표·스케줄·예선 점수 소급 변경은 제외한다. 오래된 finals-v1 채점 요청은 [이전 rubric.json](../../../docs/evaluation/legacy/rubric.json)과 [기존 채점 방법](../../../docs/evaluation/legacy/scoring-guide-v1.md)를 사용하고 현재 기준으로 재해석하지 않는다.

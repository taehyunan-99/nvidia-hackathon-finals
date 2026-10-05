# 주제 선정과 구현 평가

구현 전에는 [주제 선정 기준](topic-selection.md)으로 후보를 비교하고, 선정 후 [조합 선택](../playbooks/recipes.md) → [실행](../playbooks/README.md) → 아래 구현 평가로 진행한다. 기준의 배경이 필요할 때 [선정 과정·장단점 분석](topic-analysis.md), 과거 실행 사실은 [예선 구현 근거](bio3-review.md)를 읽는다.

주제 선정은 내부 제안인 `topic-v1`으로 평가하며 아래 구현 평가와 목적·점수를 분리한다.

| 대상 | 스킬 | 기준 / 양식 |
|---|---|---|
| 구현 전 주제 후보의 선정·보류·축소 | [$topic-rubric](../../.agents/skills/topic-rubric/SKILL.md) | [topic-v1](topic-selection.md) · [채점표](templates/topic-scorecard.json) |
| 관측 기반 판단·실제 도구·결과 | [$agent-rubric](../../.agents/skills/agent-rubric/SKILL.md) | [agent-v2](agent-rubric.md) · [채점표](templates/agent-scorecard.json) |
| 사용자 과업·상태·시각 규칙 | [$frontend-rubric](../../.agents/skills/frontend-rubric/SKILL.md) | [frontend-v2](frontend-rubric.md) · [채점표](templates/frontend-scorecard.json) |
| 두 영역의 연결·전체 준비 여부 | 두 스킬에서 통합 평가를 명시 요청한 경우 | [통합 관문](integration.md) · [채점표](templates/integration-scorecard.json) |

각 영역은 독립 100점이며 합산·평균하지 않는다. 공통 통합은 점수 없이 pass/fail/unknown으로만 확인한다. 발표 점수는 두 새 기준과 통합에서 제거했다. 역할별 평가가 다른 영역의 구현이나 추가 모델 호출을 승인하지 않는다.

[채점 방법](scoring-guide.md) · [조사 근거와 설계 이유](rubric-research.md) · [예선 구현 근거](bio3-review.md).

내부 목표는 영역별 80점·모든 항목 3 이상·미채점 없음·영역 관문 pass다. 실제 서비스 준비 완료는 두 영역과 통합 관문이 모두 충족되어야 한다. 공식 심사 배점·순위·입상 확률로 해석하지 않는다. 미제공 행사 조건은 unknown으로 기록하며, 평가 도구 준비의 미완료나 추가 조사 의무로 바꾸지 않는다.

이전 [finals-v1](legacy/rubric.md), legacy/rubric.json, [기존 채점 방법](legacy/scoring-guide-v1.md), legacy/templates/의 scorecard.json과 bio3-scorecard.json은 그대로 재계산할 수 있다. 예선 73.75점과 기존 리허설 점수를 v2로 변환하지 않는다.

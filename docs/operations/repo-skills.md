# 저장소 운영 스킬

브랜치·인계·커밋·PR·테스트·가이드를 관리하는 **repo 작업 스킬 10종**이다. 각 스킬을 명시적으로 요청한 작업에서 사용한다.

| 작업 | 스킬 | 사용 범위 / 준비 조건 |
|---|---|---|
| 작업 시작·재개 | [task-workflow](../../.agents/skills/task-workflow/SKILL.md) | 명시 호출 시 base 확인·작업 브랜치 준비; main base가 없으면 초기 Git 준비는 별도 요청 필요 |
| 세션 인계 | [handoff](../../.agents/skills/handoff/SKILL.md) | 근거/체크포인트 보존; helper는 Python 3.11+, 병렬 앱 세션은 별도 명시 요청 필요 |
| 커밋 | [commit](../../.agents/skills/commit/SKILL.md) | 요청된 staged 범위만 커밋; 최초 저장소 처리 포함 |
| PR 생성·갱신 | [pull-request](../../.agents/skills/pull-request/SKILL.md) | 요청 시 push/PR; GitHub remote/auth/base 필요 |
| 병합 후 정리 | [after-pr](../../.agents/skills/after-pr/SKILL.md) | 특정 merged PR 확인 후 해당 branch/worktree만 정리 |
| 테스트 설계·검토 | [project-test-maker](../../.agents/skills/project-test-maker/SKILL.md) | 요청 모드에 따른 테스트 전략/생성/검증; 초기 analyze는 읽기 전용 |
| 가이드 초기화 | [agentic-project-init](../../.agents/skills/agentic-project-init/SKILL.md) | 현재 7섹션 both+hook을 보존하도록 본선 적용 규칙 반영 |
| 가이드 갱신 | [update](../../.agents/skills/update/SKILL.md) | 인터뷰·충돌 검토, 기존 학습 기록 보존; 본선 형식 대응 규칙 적용 |
| 가이드 품질 점검 | [guide-audit](../../.agents/skills/guide-audit/SKILL.md) | 문서 가이드의 품질 평가; 제품 agent 루브릭과 다른 평가 |
| 주의사항 기록 | [learn](../../.agents/skills/learn/SKILL.md) | 기존 본선의 양쪽 가이드 내 학습 방식 유지; 예선 별도 파일 방식은 [참고 사본](../../.agents/skills/learn/references/bio3-variant.md)으로 보존 |

## 커밋·PR 공통 규칙

[팀 규칙](../../CONTRIBUTING.md)의 커밋·PR 절차, commit/pull-request 스킬의 Codex·Claude 진입 파일, PR 템플릿은 예선과 동일한 규칙을 유지한다. 요청 파일만 stage하고 Conventional Commits 형식을 사용하며, 검토한 SHA로 push/PR 범위를 확인한다. 팀원 검토 후 squash merge가 기본이고 실제 commit·push·PR·병합은 각각 요청 범위에서만 수행한다.

## 사용 방법

공통 본체는 `.agents/skills/`, Claude 진입은 `.claude/skills/`다. 필요한 스킬의 SKILL.md를 먼저 읽고 참조·스크립트는 공통 본체 폴더 기준으로 해석한다.
스킬 설치는 실행 승인이 아니다. 다른 체크아웃에서는 세션을 다시 열어 스킬을 확인한다. commit·push·PR·worktree 정리는 명시한 요청 범위에서만 수행한다.

## 함께 쓰는 본선 스킬

- [agent-rubric](../../.agents/skills/agent-rubric/SKILL.md): agent-v2 내부 100점으로 판단·도구·결과·실행 제어를 평가.
- [frontend-rubric](../../.agents/skills/frontend-rubric/SKILL.md): frontend-v2 내부 100점으로 과업·상태·회복·시각 규칙·접근성을 평가.
- [nvidia-ui](../../.agents/skills/nvidia-ui/SKILL.md): UI 선택과 간격·정렬·상태 표현.

예선의 `agent-evaluate`는 HER2 전용 20점/고정 데이터 의존성이 있어 요청한 repo 스킬 이관에서 제외했다. 본선 평가는 agent-rubric과 frontend-rubric으로 나누며 공통 통합은 별도 관문으로 확인한다.

## 가이드 형식

본선은 7섹션·동일 본문 both·sync hook을 사용한다. init/update는 본선 대응 규칙을 먼저 읽고, learn은 현재 가이드의 학습 영역을 사용한다. 예선 참고자료의 별도 학습 파일·CLAUDE import 방식을 자동 적용하지 않는다.

운영 방향은 [2인 개발·로컬 시연](workflow.md)을 따른다. handoff의 단계/중단 지점은 요청한 작업의 상태 기록이며 본선 시간표가 아니다.

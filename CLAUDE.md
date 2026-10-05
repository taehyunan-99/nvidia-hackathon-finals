# NVIDIA Hackathon Finals — 에이전트 작업 지도

목적: 새 본선 미션에서 도구·에이전트·스킬 조합을 빠르게 선택하고 최소 실행·검증까지 연결한다. 문서는 docs 아래에 두며 필요한 영역만 읽는다.

## 가장 빠른 진입

1. [미션에서 시작](docs/playbooks/README.md) 또는 `python3 scripts/lookup.py "미션 핵심어" --kind recipe`.
2. 결과의 guide/quickstart를 읽고 [도구](docs/catalog/tools.md)·[agent 형태](docs/catalog/agent-types.md)를 선택.
3. 스킬이 필요하면 [도메인→작업 분류](docs/catalog/skills/README.md) 또는 `lookup.py --kind skill --domain knowledge --function setup`.
4. [스킬 확보](docs/playbooks/skill-setup.md)→최소 실행→[루브릭](docs/evaluation/README.md). 설치/metadata 확인과 live 성공을 구분.

## 에이전트 흐름과 평가

[에이전트 흐름](docs/playbooks/agent-flow.md) → [루브릭](docs/evaluation/README.md) → `$agent-rubric`. 운영 방향은 [2인 개발·로컬 시연](docs/operations/workflow.md)을 따른다.

## 영역별 가이드

- [docs/AGENTS.md](docs/AGENTS.md) — 문서 지도·출처·분류 경계.
- [docs/catalog/AGENTS.md](docs/catalog/AGENTS.md) — 모델·도구·agent·스킬 원본 인덱스와 분류.
- [docs/playbooks/AGENTS.md](docs/playbooks/AGENTS.md) — 미션 조합·설치·최소 실행·성공 확인.
- [docs/evaluation/AGENTS.md](docs/evaluation/AGENTS.md) — 내부 루브릭·Bio-3 근거·평가 양식.
- [docs/operations/AGENTS.md](docs/operations/AGENTS.md) — 행사 조건·저장소 운영 방법.
- [docs/design/AGENTS.md](docs/design/AGENTS.md) — 디자인 지침과 선택 기록 위치.
- [design/AGENTS.md](design/AGENTS.md) — 조정 가능한 HTML 시안과 미리보기.
- [scripts/AGENTS.md](scripts/AGENTS.md) — 검색·확보·probe·분류·채점·검증·sync.

## 공통 경계

- 요청하지 않은 작업 완료 보고서·검증 이력·이관 보고 파일은 만들지 않는다. 작업 결과는 대화로 알리고, 저장소에는 사용법·설계·평가 기준과 실제 실행에 필요한 파일만 둔다.

- 공식 조건, 팀 제안, 실제 실행, 미검증을 구분한다. unknown은 성공이나 0으로 바꾸지 않는다.
- 전체 스킬 JSON/문서를 한꺼번에 로드하지 않는다. 검색 결과의 1~3개 원문과 필요한 참조만 읽는다.
- 원본 모델 키/인증 헤더는 출력·문서·Git에 넣지 않는다. API·GPU 사용은 명시한 범위와 예산에서 수행한다.
- 이 폴더는 독립 로컬 Git 저장소다. 작업 브랜치에서 변경하며 요청 없이 commit/push/원격 생성하지 않는다. 예선 저장소·전역 스킬은 수정하지 않는다.
- AGENTS.md/CLAUDE.md는 both 모드의 동일 본문이다. 한쪽을 수정하면 다른 쪽도 맞추거나 pre-commit sync를 사용한다. 충돌을 임의 덮어쓰지 않는다.

## 모델 호출 기본값

[모델 호출 운영 기준](docs/playbooks/model-policy.md)과 [설정 원본](docs/playbooks/model-policy.json)을 새 구현에서도 재사용한다. 실행당 실제 요청 40회·일일 4,000회·간격 15초·출력 1,024토큰·10단계가 기본이며, 재시도를 실제 요청 수에 포함한다. 설정만 복사하고 런타임 제어를 누락하지 않는다.

## CI와 검사 선택

[CI 운영 원칙](docs/operations/ci-policy.md)을 따른다. 본선 2인 팀은 로컬 자동 검사·동료 교차 검증·경량 원격 CI 보조를 사용한다. 마지막 유효 검증 이후 누적 변경을 검사하고, 10분 초과는 검증 불충분과 대체 확인으로 처리한다.

## 운영 기준

[2인 개발·로컬 시연](docs/operations/workflow.md): 공동 최소 연결 후 에이전트와 프런트·서비스로 나누고 교차 검증한다. 배포 없이 로컬 시연을 목표로 하며 개인별 담당·목표 시각은 미확정과 구분한다. [입출력 계약](docs/catalog/contracts.md) → [실행 흐름 화면](docs/design/agent-flow.md) → [리허설](docs/playbooks/rehearsal.md)을 재사용하며 [확정 디자인](docs/design/README.md)의 미세 비교는 재개하지 않는다.

## 저장소 운영 스킬

[팀 규칙](CONTRIBUTING.md)의 커밋·PR 규칙은 예선과 동일하게 유지한다. [repo 스킬 목록](docs/operations/repo-skills.md)에서 task-workflow·handoff·commit·PR·테스트·가이드 관리를 찾는다. 복사/설치는 실행 요청이 아니다.

## learn

명시적인 `$learn` 또는 `/learn`에서만 해당 영역의 LEARNED CAUTIONS를 갱신한다. Codex 본체는 `.agents/skills/learn/`, Claude 본체는 `.claude/skills/learn/`; 두 본체를 동일하게 유지한다. UI 스킬 원본은 `.agents/skills/nvidia-ui/`이며 Claude 진입 파일은 이를 참조한다.

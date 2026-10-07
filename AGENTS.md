# NVIDIA Hackathon Finals — 에이전트 작업 지도

<!-- prev: 새 미션용 조합 탐색 준비 → 2026-10-07 사용자 결정으로 한국 가족 문화체험 MVP를 구현 대상으로 확정. -->
목적: 한국 가족이 관심 분야에서 함께할 문화체험을 발견하고 후보를 비교·선택하도록 돕는다. [INTENT](docs/intent/INTENT.md)는 목적, [PRD](docs/PRD.md)는 기능 요구사항의 원본이며 [제품 문서 지도](docs/product/README.md)에서 구조·결정·데이터 근거를 찾는다. 기존 도구·스킬·실행·검증 준비 자료를 재사용한다.

## 가장 빠른 진입

<!-- prev: 참여조건 검증 중심의 요약 → 2026-10-07 update에서 INTENT의 체험 발견·비교 목적과 현재 구현 상태를 반영. -->
**현재 MVP:** 한국 가족이 관심 분야에서 함께할 문화체험을 발견·비교·선택하도록 돕고, 자녀 연령·동반 조건·날짜를 근거와 대조한다. GPS·지도·이동수단·영어 화면·현장 통역 검색은 작업 중 채택/제외할 서브미션이며 핵심 완료 조건이 아니다. OpenShell과 공통 테스트는 필수다. [설계](docs/product/agent-design.md) · [데이터 근거](docs/product/data-sources.md).

React 합성 프런트·AWS 수동 공개, 모델 없는 AWS–Brev 연결 시험, 최소 보안 하네스가 구현돼 있다. 실제 모델/API·에이전트·공통 챌린지 완주는 별도 통합 대상이다. 프런트 실행·검사는 [frontend/README.md](frontend/README.md), 보안 기반과 남은 세 통합 조치는 [OpenShell 하네스](docs/playbooks/openshell-harness.md)를 따른다.

2026-10-07 공개된 [본선 미션·공통 테스트·공식 배점·제출 요건](docs/operations/mission.md)을 먼저 확인한다. OpenShell 필수, `/hackathon` 경계 검증, **17:20 제출**을 기준으로 하며 내부 루브릭과 공식 배점을 구분한다. 반복 제출 점검은 [$submission-check](.agents/skills/submission-check/SKILL.md)를 사용한다.

<!-- prev: 미션 조합 검색부터 시작 → 2026-10-05 사용자 승인으로 주제 선정 후 조합·실행·평가 순서로 연결. -->
1. [제품 정의](docs/product/README.md)의 확정 범위를 먼저 읽고 [미션에서 시작](docs/playbooks/README.md) 또는 `python3 scripts/lookup.py "미션 핵심어" --kind recipe`. 새 후보/범위 비교에만 [주제 선정 기준](docs/evaluation/topic-selection.md)을 적용한다.
2. 결과의 guide/quickstart를 읽고 [도구](docs/catalog/tools.md)·[agent 형태](docs/catalog/agent-types.md)를 선택.
3. 스킬이 필요하면 [도메인→작업 분류](docs/catalog/skills/README.md) 또는 `lookup.py --kind skill --domain knowledge --function setup`.
4. [스킬 확보](docs/playbooks/skill-setup.md)→최소 실행→[루브릭](docs/evaluation/README.md). 설치/metadata 확인과 live 성공을 구분.

## 에이전트 흐름과 평가

[에이전트 흐름](docs/playbooks/agent-flow.md) → [루브릭](docs/evaluation/README.md) → `$agent-rubric`. 운영 방향은 [2인 개발·로컬 시연](docs/operations/workflow.md)을 따른다.

## 영역별 가이드

- [docs/AGENTS.md](docs/AGENTS.md) — 문서 지도·출처·분류 경계.
- [docs/product/AGENTS.md](docs/product/AGENTS.md) — 가족 MVP·서브미션·제품 설계·데이터 근거.
- [docs/catalog/AGENTS.md](docs/catalog/AGENTS.md) — 모델·도구·agent·스킬 원본 인덱스와 분류.
- [docs/playbooks/AGENTS.md](docs/playbooks/AGENTS.md) — 미션 조합·설치·최소 실행·성공 확인.
- [docs/evaluation/AGENTS.md](docs/evaluation/AGENTS.md) — 주제 선정·구현 평가·예선 근거·평가 양식.
- [docs/operations/AGENTS.md](docs/operations/AGENTS.md) — 행사 조건·저장소 운영 방법.
- [docs/design/AGENTS.md](docs/design/AGENTS.md) — 디자인 지침과 선택 기록 위치.
- [design/AGENTS.md](design/AGENTS.md) — 조정 가능한 HTML 시안과 미리보기.
- [scripts/AGENTS.md](scripts/AGENTS.md) — 검색·확보·probe·분류·채점·보안 하네스·연결 시험·수동 배포·sync.

`frontend/`는 별도 가이드 신설 없이 이 루트 규칙과 [기존 README](frontend/README.md)의 실행·임시 계약·mock 경계를 적용한다. `design/`의 정적 시안과 제품 프런트를 혼동하지 않는다. 사람용 개요·실행 안내는 README, 에이전트의 작업 규칙·영역 지도는 AGENTS.md를 원본으로 두고 중복 본문은 링크로 연결한다.

## 공통 경계

- 요청하지 않은 작업 완료 보고서·검증 이력·이관 보고 파일은 만들지 않는다. 작업 결과는 대화로 알리고, 저장소에는 사용법·설계·평가 기준과 실제 실행에 필요한 파일만 둔다.

- 공식 조건, 팀 제안, 실제 실행, 미검증을 구분한다. unknown은 성공이나 0으로 바꾸지 않는다.
- 전체 스킬 JSON/문서를 한꺼번에 로드하지 않는다. 검색 결과의 1~3개 원문과 필요한 참조만 읽는다.
- 원본 모델 키/인증 헤더는 출력·문서·Git에 넣지 않는다. API·GPU 사용은 명시한 범위와 예산에서 수행한다.
- 이 폴더는 독립 로컬 Git 저장소다. 작업 브랜치에서 변경하며 요청 없이 commit/push/원격 생성하지 않는다. 예선 저장소·전역 스킬은 수정하지 않는다.
<!-- prev: AGENTS.md/CLAUDE.md 동일 본문 양방향 sync → 2026-10-07 사용자 요청으로 AGENTS.md 단일 원본과 CLAUDE @ 참조로 전환. -->
- 가이드 본문은 AGENTS.md에서만 수정한다. 같은 폴더의 CLAUDE.md는 `@./AGENTS.md` 한 줄을 유지한다. hook은 가이드 참조를 검사하고 learn 스킬 사본만 동기화한다. 충돌을 임의 덮어쓰지 않는다.

## 모델 호출 기본값

[모델 호출 운영 기준](docs/playbooks/model-policy.md)과 [설정 원본](docs/playbooks/model-policy.json)을 새 구현에서도 재사용한다. 실행당 실제 요청 40회·일일 4,000회·간격 15초·출력 1,024토큰·10단계가 기본이며, 재시도를 실제 요청 수에 포함한다. 설정만 복사하고 런타임 제어를 누락하지 않는다.

## CI와 검사 선택

[CI 운영 원칙](docs/operations/ci-policy.md)을 따른다. 본선 2인 팀은 로컬 자동 검사·동료 교차 검증·경량 원격 CI 보조를 사용한다. 마지막 유효 검증 이후 누적 변경을 검사하고, 10분 초과는 검증 불충분과 대체 확인으로 처리한다.

## 운영 기준

<!-- prev: PR #3 배포 선택지 조사만 안내 → 2026-10-07 update에서 PR #6·#10의 연결 시험·합성 프런트 공개를 구분해 반영. -->
AWS와 Brev를 함께 사용할 경우 [연동 절차](docs/playbooks/aws-brev-deployment.md)를 확인한다. 초기 조사와 이후 모델 없는 연결 시험이 함께 기록돼 있다. 두루 합성 프런트의 실제 공개·수동 배포는 [프런트 운영](docs/playbooks/frontend-deployment.md), Brev 0.1.2의 합성 보안 검증은 [하네스](docs/playbooks/openshell-harness.md)를 따른다. 모델 호출·원격 자원 사용은 기존 승인 범위와 예산을 따른다.

<!-- prev: 공동 최소 연결 후 분담, 개인별 담당·목표 시각 미확정 → 2026-10-06 사용자 결정으로 11:30까지 주제·문서·계약 정리 후 단계별 분담, 15:00 공동 점검·16:00 발표 준비 시간표 반영. -->
[2인 개발·로컬 시연](docs/operations/workflow.md): 11:30까지 주제·문서·입출력 계약을 함께 정리한 뒤 단계별로 분담하고, 15:00부터 공동 점검·16:00부터 발표 준비를 진행하는 계획이다. 시간표의 A/B는 특정 팀원에게 미리 배정한 이름이 아니다. 현재는 기존 AWS의 합성 프런트와 기존 Brev VM을 사용하며 새 인스턴스 생성·예산 확대를 전제하지 않는다. [입출력 계약](docs/catalog/contracts.md) → [실행 흐름 화면](docs/design/agent-flow.md) → [리허설](docs/playbooks/rehearsal.md)을 재사용하며 [확정 디자인](docs/design/README.md)의 미세 비교는 재개하지 않는다. 이번 보안 개발은 본선·챌린지 최소 범위로 제한하고 이후 작업은 실제 패키지 배치·에이전트 연결·최종 정책 재검증에 집중한다.

## 저장소 운영 스킬

[팀 규칙](CONTRIBUTING.md)의 커밋·PR 규칙은 예선과 동일하게 유지한다. [repo 스킬 목록](docs/operations/repo-skills.md)에서 task-workflow·handoff·commit·PR·테스트·가이드 관리를 찾는다. 복사/설치는 실행 요청이 아니다.

## learn

명시적인 `$learn` 또는 `/learn`에서만 해당 영역의 LEARNED CAUTIONS를 갱신한다. Codex 본체는 `.agents/skills/learn/`, Claude 본체는 `.claude/skills/learn/`; 두 본체를 동일하게 유지한다. UI 스킬 원본은 `.agents/skills/nvidia-ui/`이며 Claude 진입 파일은 이를 참조한다.

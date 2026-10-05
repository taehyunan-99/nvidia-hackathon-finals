# NVIDIA Hackathon Finals

새 미션에서 **어떤 조합을 쓸지 고르고, 어떻게 실행·검증할지 빠르게 찾는 준비 저장소**.
문서는 [docs](docs/README.md)에 구조화했다. 공식 조건은 [행사 안내](docs/operations/event.md)에 보존하며, 합의한 작업 방향은 [2인 개발·로컬 시연 운영](docs/operations/workflow.md)에서 찾는다.

## 먼저 찾을 것

| 지금 필요한 것 | 읽을 곳 |
|---|---|
| 두 사람이 구현·통합·시연한다 | [2인 개발·로컬 시연 운영](docs/operations/workflow.md) |
| 프런트와 에이전트의 데이터를 맞춘다 | [입출력 계약·schema·예시 JSON](docs/catalog/contracts.md) · [다른 조합 9개](docs/catalog/contracts/combinations.md) |
| 도구 선택·분석 과정을 화면에 붙인다 | [재사용 컴포넌트](docs/design/agent-flow.md) · [실행 화면](design/agent-flow.html) |
| 검색부터 화면까지 작게 점검한다 | [로컬 리허설 명령과 성공 기준](docs/playbooks/rehearsal.md) |
| 에이전트가 문제를 어떻게 해결하는가 | [공통 에이전트 흐름](docs/playbooks/agent-flow.md) |
| 변경 후 어떤 검사를 할지 결정한다 | [CI 운영 원칙](docs/operations/ci-policy.md) |
| 브랜치·인계·커밋·PR·가이드 작업 | [저장소 운영 스킬 10종](docs/operations/repo-skills.md) |
| 에이전트·프런트를 채점하고 개선한다 | [평가 진입](docs/evaluation/README.md) · `$agent-rubric` · `$frontend-rubric` |
| 미션을 받았고 조합을 골라야 한다 | [미션별 실행 안내](docs/playbooks/README.md) |
| 어떤 agent 형태가 맞는지 판단한다 | [9개 형태 비교](docs/catalog/agent-types.md) |
| 도구의 역할·조건·실행법을 찾는다 | [18개 도구 카드](docs/catalog/tools.md) |
| 스킬이 많아 필요한 것만 찾는다 | [11개 도메인 → 7개 작업 목적 → 스킬](docs/catalog/skills/README.md) |
| 스킬을 받아 개발 agent에 연결한다 | [설치·고정 버전 확보·발견 확인](docs/playbooks/skill-setup.md) |

프로젝트 루트에서 다음처럼 조회한다. 검색은 인터넷·모델·추가 Python 패키지 없이 동작한다.

```sh
python3 scripts/lookup.py "문서" --kind recipe
python3 scripts/lookup.py --show recipe:documents
python3 scripts/lookup.py --domain knowledge --function setup --kind skill
```

검색 결과의 `guide` → `quickstart` → `성공 기준`을 따라간다. 정확한 이름을 알면 `--show`에 결과 ID를 주고, 못 찾으면 필터를 풀거나 영어 제품명으로 검색한다.

## 문서 구조

- [docs/catalog](docs/catalog/README.md) — 409개 스킬의 원본 metadata, 도메인/작업별 탐색, agent·도구 카드.
- [docs/playbooks](docs/playbooks/README.md) — 10개 미션 조합, 9개 최소 실행 안내, 하네스·예제·스킬 확보법.
- [docs/evaluation](docs/evaluation/rubric.md) — 내부 100점 루브릭, Bio-3 분석, 평가 양식.
- [docs/operations](docs/operations/event.md) — 행사·준비 항목, [both 동기화](docs/operations/guide-sync.md).
- [docs/design](docs/design/README.md) — 디자인 스킬과 [UI 비교 시안](design/playground.html) 진입.

실행 코드는 `scripts/`, 정적 UI는 `design/`, 공통 개발 스킬은 `.agents/skills/`, Claude 진입은 `.claude/skills/`에 있다. 작업 전 [AGENTS.md](AGENTS.md) 또는 동일 내용의 [CLAUDE.md](CLAUDE.md)를 읽는다.

## 사용 전 확인

카탈로그는 고정 버전의 스킬 metadata다. 필요한 1~3개 원문만 읽고 실제 계정의 API/GPU 접근과 호환성을 확인한다. 문서 존재나 설치 상태를 실행 성공으로 해석하지 않는다.
다른 PC에서 사용할 때는 [hook 활성화](docs/operations/guide-sync.md)를 따른다. 디자인 세부 기준과 상태 표시는 확정했다. 미정 장식·공식 미확정 조건·시간표 제안은 확정 운영 기준과 구분한다.

## 로컬 검사

`python3 scripts/validate.py`는 링크·원본 인덱스 범위·분류·조합 연결·both 가이드를 검사한다.
`python3 -m unittest discover -s scripts -p 'test_*.py'`는 검색·채점·모델 응답 검사·동기화 보호 동작을 검사한다.
`python3 scripts/probe_nim.py`는 기본 dry-run이며 실제 호출은 `--live`에서만 수행한다.

본선 점수 활용: [진출 요인 추가 분석](docs/evaluation/bio3-review.md) → [루브릭 채점과 다음 개선](docs/evaluation/scoring-guide.md).

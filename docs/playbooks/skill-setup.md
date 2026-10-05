# 스킬 찾기 → 받기 → agent에 연결

**스킬 설치와 제품 설치는 별개**다. SKILL.md는 사용법이며 NIM 키/컨테이너/SDK가 자동으로 준비되지 않는다.

## 1. 찾기

프로젝트 루트에서 `python3 scripts/lookup.py "retriever" --kind skill`을 실행한다. 결과의 `name`이 실제 설치 선택 이름이다. 예: 폴더 `bionemo-boltz2-nim`의 이름은 `boltz2-nim`이다.
한 번에 해당 미션의 핵심 1~3개부터 선택한다. 전체 409개를 agent context에 주입하지 않는다.

## 2. 최신 공개 스킬 설치 — 공식 CLI

Node/npm과 현재 `skills` CLI가 필요하다. 아래는 실행 안내이며 이번 준비 작업에서 NVIDIA 스킬을 일괄 설치하지 않았다.

```sh
npx skills --version
npx skills add NVIDIA/skills --list
npx skills add NVIDIA/skills --skill nemo-retriever --agent codex --agent claude-code
```

NAT 전용 예: `npx skills add NVIDIA/NeMo-Agent-Toolkit --skill nat-installation --agent codex --agent claude-code`.
설치 명령은 실행 위치의 프로젝트를 대상으로 한다. `--global`을 추가하지 않는다. 최신 CLI의 카탈로그 결과와 [공식 설치 문서](https://docs.nvidia.com/skills/advanced-install)가 우선한다.

## 3. 확인한 버전 그대로 확보 — 이 프로젝트의 보조 스크립트

```sh
python3 scripts/fetch_skill.py nat-installation --dest reference-skills
```

전체 인덱스의 고정 commit에서 해당 폴더 전체와 repository 라이선스를 받는다. SHA256을 기록하며 **설치 스크립트를 실행하지 않는다**. 같은 목적지에 이미 있으면 덮어쓰지 않는다.
`reference-skills/<folder>/`는 참고 사본이며 agent discovery 경로가 아니다. 내용/참조/라이선스를 확인한 뒤 필요한 클라이언트의 프로젝트 스킬 디렉터리로 전체 폴더를 복사한다. 두 클라이언트를 함께 쓰면 두 경로 또는 공식 CLI를 이용하고 서로 다른 버전이 섞이지 않게 한다.

원문이 다른 경로의 SDK·예제·문서를 요구하면 그 의존성까지 따로 확인한다. 스킬 폴더 다운로드가 모든 제품 의존성을 포함한다는 뜻은 아니다.

## 4. 발견/사용 확인

- Codex 대상 `.agents/skills/<name>/SKILL.md`, Claude 대상 `.claude/skills/<name>/SKILL.md`를 확인한다. 실제 폴더명은 설치 결과를 따른다.
- agent가 스킬 목록을 다시 불러오도록 새 세션/클라이언트 reload를 이용한다. 파일 존재만으로 현재 대화에 로드됐다고 단정하지 않는다.
- “선택한 스킬의 버전·전제조건을 읽고 최소 입력 1건과 기대 출력을 정리해줘”로 원문 연결을 확인한다.
- 제품 SDK/endpoint 준비 후 실제 도구 실행 결과를 따로 남긴다.

## 실패 시

목록에 이름이 없으면 폴더명이 아닌 frontmatter 이름인지 확인한다. 참조 파일이 없으면 단일 SKILL.md만 복사했는지 확인한다. 설치가 깨지면 전역 환경을 변경하기 전에 프로젝트 범위/CLI 버전/원문을 확인한다.

# both 가이드 운영

both 모드의 가이드를 관리한다. 루트와 8개 영역의 AGENTS.md/CLAUDE.md 9쌍, learn SKILL.md 1쌍을 합쳐 10쌍을 관리한다.

## 수정·동기화

1. 가이드 한쪽을 수정하고 내용을 검토한다. 양쪽을 직접 같은 내용으로 수정해도 된다.
2. 사용자 의도대로 commit을 준비할 때 변경한 쪽을 stage한다.
3. pre-commit이 staged 방향으로 상대 파일을 동기화하고 함께 stage한다.

`bash scripts/sync-agents-md.sh --check`는 쓰기 없이 동일 여부를 확인한다. 인자 없는 실행은 동기화/상대 파일 staging을 수행하므로 단순 검사에는 `--check`를 사용한다.

## 보존 장치

Python 동기화 도구는 **부분 staged 수정, 반대쪽 unstaged 수정/삭제, 서로 다른 양쪽 staged, 방향 없는 불일치**에서 중단한다. 모든 쌍을 먼저 검사하여 후반 충돌 때문에 앞부분만 바뀌는 일을 피한다.
가이드 삭제도 자동으로 결정하지 않는다. 쌍 목록 `scripts/guide-pairs.json`을 의도에 맞게 함께 수정한다.

## 설치와 다른 PC

hook은 `git config --local core.hooksPath .githooks`로 활성화한다. Git 설정은 clone으로 이동하지 않으므로 새 checkout에서 한 번 실행한다. Python 3.9+와 Bash/Git이 필요하며 Windows는 Git Bash/호환 Python을 사용한다; Windows 실검증은 아직 하지 않았다.

Git hook 실행 여부와 가이드가 현재 일치하는지는 별개다. 작업 중에도 `--check`를 사용한다. hook은 commit 명령을 실행하지 않는다.

## learn과 UI 스킬

learn은 `.agents/skills/learn`과 `.claude/skills/learn`에 설치했다. 명시 `$learn`/`/learn` 호출에서만 동작하며 원본 스킬의 확인 절차를 유지한다.
UI 스킬은 `.agents/skills/nvidia-ui`가 원본이고 `.claude/skills/nvidia-ui/SKILL.md`는 상대 경로로 원본을 읽는다. 두 UI 규칙 사본을 따로 유지하지 않는다.


## 파일명 대소문자

작업 지침은 정확히 AGENTS.md/CLAUDE.md로 저장한다. 일반 설명 문서는 agent-types.md, 스킬 도메인 안내는 agent-workflows.md를 사용한다. macOS의 대소문자 비구분 환경에서는 agents.md와 AGENTS.md가 같은 파일이므로 소문자 이름을 일반 문서에 사용하지 않는다. 검증기와 동기화 도구는 실제 디렉터리 항목의 대소문자까지 검사한다.

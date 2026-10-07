# 가이드 참조와 스킬 사본 운영

<!-- prev: AGENTS.md/CLAUDE.md 동일 본문·양방향 동기화 → 2026-10-07 사용자 요청으로 AGENTS.md 단일 원본·CLAUDE @ 참조로 전환. -->
가이드 본문은 **AGENTS.md 한 곳**에서 관리한다. 같은 폴더의 CLAUDE.md는 아래 한 줄로 원본을 가져온다.

```text
@./AGENTS.md
```

루트와 9개 영역의 가이드 참조 10쌍, learn SKILL.md 동일 사본 1쌍을 `scripts/guide-pairs.json`에서 관리한다. 새 영역을 추가하면 해당 폴더의 AGENTS.md·CLAUDE.md와 쌍 목록을 함께 갱신한다.

## 수정·검사

1. 가이드 규칙과 기존 학습 기록은 AGENTS.md에서만 수정한다. CLAUDE.md에 본문을 복제하거나 덧붙이지 않는다.
2. `python3 scripts/validate.py`와 `bash scripts/sync-agents-md.sh --check`로 링크·가이드 참조·learn 사본을 검사한다. 두 명령은 staging을 변경하지 않는다.
3. commit 준비 시 요청한 변경만 stage한다. hook은 작업 트리와 index의 가이드 참조가 유효한지 검사한다. 잘못된 CLAUDE.md를 자동 덮어쓰거나 AGENTS.md로 역복사하지 않는다.
4. learn 스킬 본체 자체를 수정할 때만 기존 staged 방향의 사본 동기화가 동작한다. 이는 learn 실행이나 학습 기록 추가가 아니다.

인자 없는 `bash scripts/sync-agents-md.sh`는 learn 사본의 쓰기·상대 파일 staging을 수행할 수 있다. 단순 확인에는 `--check`를 사용한다. 가이드 참조를 작업 트리에서만 고치고 index에 잘못된 본문을 남긴 경우 hook은 중단한다.

## 보존 장치

가이드 참조는 정확한 `@./AGENTS.md`와 원본 존재를 확인하고, symlink·저장소 밖 경로·파일명 대소문자 오류를 거부한다. 참조 검사에 실패하면 learn 사본의 계획된 변경도 실행하지 않는다.

learn 사본 동기화는 **부분 staged 수정, 반대쪽 unstaged 수정/삭제, 서로 다른 양쪽 staged, 방향 없는 불일치**에서 중단한다. 가이드·스킬 삭제나 기존 내용의 충돌을 자동으로 해결하지 않는다.

## 설치와 다른 PC

hook은 `git config --local core.hooksPath .githooks`로 활성화한다. Git 설정은 clone으로 이동하지 않으므로 새 checkout에서 한 번 실행한다. Python 3.9+와 Bash/Git이 필요하며 Windows는 Git Bash/호환 Python을 사용한다; Windows 실검증은 아직 하지 않았다. handoff helper의 Python 3.11+ 조건은 별도로 유지한다.

hook은 commit 명령을 실행하지 않는다. 로컬 검사 통과와 실제 Claude 클라이언트의 로딩 관측도 구분한다.

## learn과 UI 스킬

learn의 Codex/Claude 본체 사본은 유지하되, 명시 호출 시 메모를 쓸 대상은 AGENTS.md의 기존 7번 학습 영역이다. CLAUDE.md의 참조 한 줄은 수정하지 않는다. 기존 LEARNED CAUTIONS는 이번 참조 전환에서 추가·삭제·내용 변경하지 않는다.

UI 스킬은 `.agents/skills/nvidia-ui`가 원본이고 `.claude/skills/nvidia-ui/SKILL.md`는 이를 참조한다. 스킬 wrapper와 CLAUDE.md의 가이드 import는 서로 다른 진입 방식이다.

## 파일명 대소문자

작업 지침은 정확히 AGENTS.md/CLAUDE.md로 저장한다. 일반 설명 문서는 agent-types.md, 스킬 도메인 안내는 agent-workflows.md를 사용한다. macOS의 대소문자 비구분 환경에서는 agents.md와 AGENTS.md가 같은 파일이므로 소문자 이름을 일반 문서에 사용하지 않는다.

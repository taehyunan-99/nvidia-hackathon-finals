---
name: agentic-project-init
description: "명시 호출 시 프로젝트 영역 지도를 초기화한다. 본선 저장소에서는 승인된 7섹션 AGENTS.md 원본·CLAUDE.md 참조와 검사 hook을 보존한다."
---

# Agentic Project Init

예선의 영역 탐지/가이드 초기화 스킬을 본선의 기존 구조에 맞춘 사본이다. [본선 형식](references/finals-compatibility.md)을 먼저 읽는다. 설치 요청만으로 실행하지 않는다.

1. `claude|agents|both` 인자를 확인한다. 없으면 선택을 묻는다. 기존 프로젝트의 모드를 바꾸려는 요청이 아니면 현재 AGENTS 원본·CLAUDE 참조 방식을 유지한다.
2. Git과 기존 가이드·hook·learn의 상태를 확인한다. 기존 파일 재생성/정책 전환을 자동 수행하지 않는다. 검사 hook을 설정할 Git이 없으면 초기화 범위를 확인한다.
3. [영역 탐지](references/area-detection.md)로 필요한 영역을 제안하고 사용자의 범위/기존 승인에 맞춘다. 불명확한 영역은 확인한다.
4. 기존 가이드의 WHAT/CONTENTS/HOW/HOW NOT/WHERE/WHY/LEARNED CAUTIONS 7섹션에 맞춰 초안을 제시한다. 확인되지 않은 도메인 규칙은 추정으로 표시한다.
5. 새 가이드를 만들 때 루트 지도와 영역 링크를 갱신한다. AGENTS.md가 본문 원본이며 CLAUDE.md는 `@./AGENTS.md`만 포함하고 일반 문서는 agent-types.md 등 별도 이름을 쓴다.
6. 기존 learn을 보존한다. 가이드 참조 쌍은 scripts/guide-pairs.json에 등록하고 현재 검사 helper/hook을 사용한다. 별도 학습 파일 방식으로 자동 전환하지 않는다.
7. `python3 scripts/validate.py`, `bash scripts/sync-agents-md.sh --check`로 확인한다. 자동 commit/push하지 않는다.

번들 assets는 예선 원본을 함께 보존한 참고자료다. 현재 구조의 출력 규격은 기존 본선 가이드와 finals-compatibility.md가 우선하며, 승인되지 않은 형식 전환을 자동 실행하지 않는다.

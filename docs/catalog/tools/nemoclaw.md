# NemoClaw

선택한 agent를 관리된 inference·격리 환경에서 운영

## 선택 조건

지원 host/container·agent variant·provider, 해당 variant의 quickstart 확인.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/runtime.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:nemoclaw`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [nemoclaw-user-guide](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemoclaw-user-guide/SKILL.md) — 폴더 `nemoclaw-user-guide`

## 성공 기준과 실패 대안

- 성공 확인: sandbox에서 허용된 작업 한 건과 차단 동작 확인.
- 축소/대안: NAT 웹 agent만 필요한 경우 런타임 계층 추가를 미룸.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“선택한 agent를 관리된 inference·격리 환경에서 운영에 NemoClaw가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://github.com/NVIDIA/NemoClaw) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

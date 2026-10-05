# OpenShell

agent 실행의 파일/네트워크/프로세스 경계를 관리

## 선택 조건

host/runtime 정책, provider, 파일·네트워크 허용 범위 확인.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/runtime.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:openshell`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [nemotron-policy-generator](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemotron-policy-generator/SKILL.md) — 폴더 `nemotron-policy-generator`

## 성공 기준과 실패 대안

- 성공 확인: 허용 파일/도메인은 동작하고 금지된 접근은 거부.
- 축소/대안: 코드 실행이 없는 읽기 전용 도구로 범위 축소.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“agent 실행의 파일/네트워크/프로세스 경계를 관리에 OpenShell가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://github.com/NVIDIA/OpenShell) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

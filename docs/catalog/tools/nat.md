# NeMo Agent Toolkit

모델·함수·MCP를 workflow로 연결하고 실행/관측

## 선택 조건

Python 호환 버전+langchain extra. 예선 설치는 1.9.0 확인, 새 환경 호환성은 별도.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/nat.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:nat`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [nat-installation](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-installation/SKILL.md) — 폴더 `nat-installation`
- [nat-workflow-creation](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-workflow-creation/SKILL.md) — 폴더 `nat-workflow-creation`
- [nat-tools-and-functions](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-tools-and-functions/SKILL.md) — 폴더 `nat-tools-and-functions`

## 성공 기준과 실패 대안

- 성공 확인: nat CLI, 구성 로딩, 실제 도구 호출 후 종료.
- 축소/대안: 단일 agent·함수 1개부터. 프레임워크 교체보다 버전/등록 문제 해결.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“모델·함수·MCP를 workflow로 연결하고 실행/관측에 NeMo Agent Toolkit가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://github.com/NVIDIA/NeMo-Agent-Toolkit) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

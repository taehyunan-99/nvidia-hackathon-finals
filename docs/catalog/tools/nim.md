# Nemotron / NIM

목표와 관측에서 다음 행동을 선택하는 모델·추론 endpoint

## 선택 조건

hosted: API 권한·모델별 tool-calling 확인. self-host: 모델별 GPU/메모리·라이선스 확인.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/nat.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:nim`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [nat-agent-configuration](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-agent-configuration/SKILL.md) — 폴더 `nat-agent-configuration`

## 성공 기준과 실패 대안

- 성공 확인: 실제 tool call 인자·반환 관측·종료와 모델 ID를 기록.
- 축소/대안: 같은 endpoint에서 사용 가능한 모델을 확인; 연결 실패를 mock 성공으로 대체하지 않음.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“목표와 관측에서 다음 행동을 선택하는 모델·추론 endpoint에 Nemotron / NIM가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://build.nvidia.com/explore/discover) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

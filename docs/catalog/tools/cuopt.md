# cuOpt

배차·경로 또는 LP/MILP/QP 제약 최적화

## 선택 조건

Linux NVIDIA GPU/remote server. CUDA 12/13 패키지와 runtime 일치, solver 종류 선택.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/optimization.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:cuopt`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [cuopt-install](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/cuopt-install/SKILL.md) — 폴더 `cuopt-install`
- [cuopt-numerical-optimization-formulation](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/cuopt-numerical-optimization-formulation/SKILL.md) — 폴더 `cuopt-numerical-optimization-formulation`
- [cuopt-numerical-optimization-api](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/cuopt-numerical-optimization-api/SKILL.md) — 폴더 `cuopt-numerical-optimization-api`
- [cuopt-routing-api-python](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/cuopt-routing-api-python/SKILL.md) — 폴더 `cuopt-routing-api-python`

## 성공 기준과 실패 대안

- 성공 확인: feasible 상태와 목적값·각 제약을 독립적으로 다시 계산.
- 축소/대안: 작은 문제/규칙 baseline. 자연어 추천을 최적화 완료로 표시하지 않음.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“배차·경로 또는 LP/MILP/QP 제약 최적화에 cuOpt가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://github.com/NVIDIA/cuopt) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

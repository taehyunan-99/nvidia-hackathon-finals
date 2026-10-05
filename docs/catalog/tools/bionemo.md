# BioNeMo NIM

구조/분자 생성·예측 전문 도구

## 선택 조건

모델별 endpoint·입력 제약·키·좌표 파서 및 독립 검증 자료.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/biology.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:bionemo`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [boltz2-nim](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-boltz2-nim/SKILL.md) — 폴더 `bionemo-boltz2-nim`
- [diffdock-nim](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-diffdock-nim/SKILL.md) — 폴더 `bionemo-diffdock-nim`
- [genmol-nim](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-genmol-nim/SKILL.md) — 폴더 `bionemo-genmol-nim`

## 성공 기준과 실패 대안

- 성공 확인: 구조·사슬·서열 대응과 출처를 검사; 추론 한계 표시.
- 축소/대안: 공개 구조 재사용/분자 규칙 검산. 새 예측 성능은 별도 평가.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“구조/분자 생성·예측 전문 도구에 BioNeMo NIM가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://build.nvidia.com/explore/discover) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

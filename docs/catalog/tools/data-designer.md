# NeMo Data Designer

schema·생성 규칙으로 합성 평가 데이터 작성

## 선택 조건

Python 패키지와 모델 provider. 생성 비용/원본 자료 사용 범위 확인.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/validation.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:data-designer`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [data-designer](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/data-designer/SKILL.md) — 폴더 `data-designer`

## 성공 기준과 실패 대안

- 성공 확인: 작은 생성 결과의 schema·검증기·수동 의미 검사.
- 축소/대안: 수동 8사례부터 시작; 합성 데이터를 독립 실험 정답으로 취급하지 않음.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“schema·생성 규칙으로 합성 평가 데이터 작성에 NeMo Data Designer가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://github.com/NVIDIA-NeMo/DataDesigner) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

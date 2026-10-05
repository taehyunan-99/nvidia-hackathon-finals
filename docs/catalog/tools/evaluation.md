# NAT evaluation / telemetry

고정 입력으로 작업 성공·도구 경로·지연 비교

## 선택 조건

nat eval은 해당 버전 eval extra 필요. evaluator와 데이터 형식 확인.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/validation.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:evaluation`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [nat-evaluation](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-evaluation/SKILL.md) — 폴더 `nat-evaluation`
- [nat-telemetry](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-telemetry/SKILL.md) — 폴더 `nat-telemetry`
- [nat-optimization](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-optimization/SKILL.md) — 폴더 `nat-optimization`

## 성공 기준과 실패 대안

- 성공 확인: 실패를 분모에 유지, baseline과 동일 입력, trace→판정 연결.
- 축소/대안: JSONL과 결정적 검사부터; LLM judge만으로 성공 확정하지 않음.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“고정 입력으로 작업 성공·도구 경로·지연 비교에 NAT evaluation / telemetry가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://docs.nvidia.com/nemo/agent-toolkit/latest/improve-workflows/evaluate.html) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

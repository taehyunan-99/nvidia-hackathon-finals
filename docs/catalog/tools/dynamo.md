# Dynamo

여러 inference 요청의 서빙/라우팅 성능 조정

## 선택 조건

GPU·선택 backend·배포 recipe 및 실측 부하가 필요.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/specialized.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:dynamo`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [dynamo-recipe-runner](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/dynamo-recipe-runner/SKILL.md) — 폴더 `dynamo-recipe-runner`
- [dynamo-router-starter](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/dynamo-router-starter/SKILL.md) — 폴더 `dynamo-router-starter`
- [dynamo-troubleshoot](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/dynamo-troubleshoot/SKILL.md) — 폴더 `dynamo-troubleshoot`

## 성공 기준과 실패 대안

- 성공 확인: 동일 입력 부하에서 오류율·지연·처리량 기록.
- 축소/대안: 단일 endpoint가 충분하면 추가하지 않음.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“여러 inference 요청의 서빙/라우팅 성능 조정에 Dynamo가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://github.com/NVIDIA/skills/tree/main/skills/dynamo-recipe-runner) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

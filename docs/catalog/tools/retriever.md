# NeMo Retriever

문서·표·이미지를 추출하고 출처가 있는 검색 결과 생성

## 선택 조건

원격 NIM/service client와 local GPU 모드 구분. 선택한 모델 접근 확인.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/retrieval.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:retriever`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [nemo-retriever](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-retriever/SKILL.md) — 폴더 `nemo-retriever`
- [nemo-retriever-mcp](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-retriever-mcp/SKILL.md) — 폴더 `nemo-retriever-mcp`

## 성공 기준과 실패 대안

- 성공 확인: 관련 문서/페이지와 답 없는 질문의 빈 결과를 확인.
- 축소/대안: 문서 3개와 단순 검색으로 축소하고 원문 위치 유지.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“문서·표·이미지를 추출하고 출처가 있는 검색 결과 생성에 NeMo Retriever가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://github.com/NVIDIA/NeMo-Retriever) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

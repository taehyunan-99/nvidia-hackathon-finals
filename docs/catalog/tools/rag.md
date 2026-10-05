# RAG Blueprint

검색·생성·검증을 묶은 참조 애플리케이션

## 선택 조건

별도 blueprint checkout, Docker/Compose 또는 library 경로. GPU/remote NIM 선택.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/retrieval.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:rag`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [rag-blueprint](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/rag-blueprint/SKILL.md) — 폴더 `rag-blueprint`
- [rag-eval](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/rag-eval/SKILL.md) — 폴더 `rag-eval`
- [rag-perf](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/rag-perf/SKILL.md) — 폴더 `rag-perf`

## 성공 기준과 실패 대안

- 성공 확인: ingest 완료→query→원문 인용 대조; quality와 latency 분리.
- 축소/대안: 전체 stack 설치가 지연되면 Retriever+작은 agent 조합.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“검색·생성·검증을 묶은 참조 애플리케이션에 RAG Blueprint가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://github.com/NVIDIA-AI-Blueprints/rag) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

# Video Search and Summarization

영상 검색·시각 질의·시간 구간 요약

## 선택 조건

실행 중인 VSS profile, 모델/저장소/영상 접근·GPU 조건 확인.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/video.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:vss`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [vss-deploy-profile](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-deploy-profile/SKILL.md) — 폴더 `vss-deploy-profile`
- [vss-search-archive](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-search-archive/SKILL.md) — 폴더 `vss-search-archive`
- [vss-ask-video](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-ask-video/SKILL.md) — 폴더 `vss-ask-video`
- [vss-summarize-video](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-summarize-video/SKILL.md) — 폴더 `vss-summarize-video`

## 성공 기준과 실패 대안

- 성공 확인: 질문에 해당하는 프레임·시간 구간을 사람이 대조.
- 축소/대안: 짧은 clip 한 개로 축소. 메타데이터 조회를 시각 확인이라고 부르지 않음.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“영상 검색·시각 질의·시간 구간 요약에 Video Search and Summarization가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

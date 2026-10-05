# Nemotron Speech / Riva

음성 인식·합성·번역을 업무 도구와 연결

## 선택 조건

선택 모델의 한국어·오디오 포맷·sample rate·hosted/self-host 지원 확인.

## 바로 사용할 경로

1. [최소 실행 안내](../../playbooks/quickstarts/speech.md)를 읽고 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:speech`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [nemotron-speech](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemotron-speech/SKILL.md) — 폴더 `nemotron-speech`
- [nemotron-voice-agent-builder](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemotron-voice-agent-builder/SKILL.md) — 폴더 `nemotron-voice-agent-builder`

## 성공 기준과 실패 대안

- 성공 확인: 짧은 발화 전사와 실제 업무 처리; 무음/잡음·언어 실패 확인.
- 축소/대안: 텍스트 입력 경로 유지; ASR 성공만으로 업무 완료를 선언하지 않음.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“음성 인식·합성·번역을 업무 도구와 연결에 Nemotron Speech / Riva가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://docs.nvidia.com/nim/speech/latest/) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

# Brev

GPU 환경을 마련해 원격 개발·컨테이너 실행

## 선택 조건

지급 계정/크레딧·GPU·디스크·포트·종료 조건 확인.

## 바로 사용할 경로

1. [대회 당일 사용 가이드](../../playbooks/brev-event-guide.md)에서 API·GPU 선택과 크레딧·실행·종료 순서를 확인하고, [최소 실행 안내](../../playbooks/quickstarts/runtime.md)로 배치 경로를 선택한다.
2. 필요한 스킬만 아래 링크 또는 `python3 scripts/lookup.py --show tool:brev`로 조회한다.
3. 준비된 작은 입력으로 실행하고 아래 성공 기준을 확인한다.

## 관련 스킬

- [tao-run-on-brev](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-run-on-brev/SKILL.md) — 폴더 `tao-run-on-brev`

## 성공 기준과 실패 대안

- 성공 확인: SSH/컨테이너/GPU 확인 후 해당 도구의 최소 추론.
- 축소/대안: hosted API 우선. GPU 미지급이면 GPU 전용 조합 보류.
- 확인 수준: 공식 자료/스킬 조사. 본선 계정·실제 GPU/API 실행은 미검증.

## 첫 작업 지시 예시

“GPU 환경을 마련해 원격 개발·컨테이너 실행에 Brev가 적합한지 입력/환경부터 확인하고, 필요한 스킬과 최소 실행 경로·검증 방법을 제시해줘. 연결하지 못한 단계는 미검증으로 남겨줘.”

[공식 원문](https://docs.nvidia.com/brev/getting-started/overview) · 조사 2026-10-03. 재현할 스킬 버전은 [전체 인덱스](../skills-index.json)를 따른다.

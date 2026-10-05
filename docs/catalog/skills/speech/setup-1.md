# 음성·대화 / 설치·배포 / 1

[도메인으로](../domains/speech.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `digital-health-clinical-asr-setup` | Stage 1 of Clinical ASR Flywheel. Use when bootstrapping a cycle: NVCF+MW disclosure, NVIDIA_API_KEY check, deps install, TTS+ASR smoke test. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/digital-health-clinical-asr-setup/SKILL.md) |
| `nemotron-speech` | Routes NVIDIA Nemotron Speech (Formerly Riva) NIM tasks — deploys, runs, and tests ASR, TTS, and NMT NIMs on build.nvidia.com or self-hosted. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemotron-speech/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/digital-health-clinical-asr-setup"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

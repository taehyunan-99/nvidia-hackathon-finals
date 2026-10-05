# 음성·대화 / 성능·조정 / 1

[도메인으로](../domains/speech.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `digital-health-clinical-asr-finetune` | Stage 4 of the Clinical ASR Flywheel. Use when priority KER is above 0.3 to run stock NeMo SFT on Parakeet TDT v2 and offline cycle N+1 re-eval. NOT f… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/digital-health-clinical-asr-finetune/SKILL.md) |
| `nemotron-asr-finetune` | Orchestration skill for NVIDIA Nemotron Speech (Riva) / NeMo ASR domain and language adaptation. Given a goal like "improve/fine-tune ASR for my domai… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemotron-asr-finetune/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/digital-health-clinical-asr-finetune"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

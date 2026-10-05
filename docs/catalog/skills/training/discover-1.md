# 모델 학습·조정 / 탐색·선택 / 1

[도메인으로](../domains/training.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `nemo-mbridge-perf-moe-dispatcher-selection` | Choose the right MoE token dispatcher (`alltoall`, DeepEP, or HybridEP) for the hardware, EP degree, and optimization stage. Summarizes patterns from … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-mbridge-perf-moe-dispatcher-selection/SKILL.md) |
| `nemo-mbridge-recipe-recommender` | Recommend and customize Megatron Bridge library and benchmark recipes for a user's model, GPU count, hardware, sequence length, and pretrain/SFT/PEFT … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-mbridge-recipe-recommender/SKILL.md) |
| `nemo-rl-docs` | Documentation conventions for NeMo-RL. Covers docs/index.md updates and docstring format. Do NOT use for: bug fixes, test fixes, dependency bumps, ref… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-rl-docs/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/nemo-mbridge-perf-moe-dispatcher-selection"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

# 생명과학·의료 / 성능·조정 / 1

[도메인으로](../domains/biology.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `digital-health-clinical-asr-finetune` | Stage 4 of the Clinical ASR Flywheel. Use when priority KER is above 0.3 to run stock NeMo SFT on Parakeet TDT v2 and offline cycle N+1 re-eval. NOT f… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/digital-health-clinical-asr-finetune/SKILL.md) |
| `kermt-finetune` | Finetune a pretrained KERMT encoder on a labeled CSV. Validate the checkpoint and data, prepare features, and run containerized training. Use a local … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-kermt-finetune/SKILL.md) |
| `kermt-monitor` | Check progress for a detached KERMT run (pretrain, finetune, or any kermt_run_detached invocation). Reads run.json, queries docker for container state… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-kermt-monitor/SKILL.md) |
| `molmim-nim` | Use this skill for MolMIM, NVIDIA's BioNeMo NIM microservice for small-molecule latent-space generation and optimization. Invoke for MolMIM, molecular… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-molmim-nim/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/digital-health-clinical-asr-finetune"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

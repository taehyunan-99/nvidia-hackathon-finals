# 생명과학·의료 / 설치·배포 / 1

[도메인으로](../domains/biology.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `boltz2-nim` | Use Boltz2 NIM for biomolecular structure prediction and binding affinity. Invoke for Boltz2, protein structures, protein-ligand/DNA/RNA complexes, SM… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-boltz2-nim/SKILL.md) |
| `digital-health-clinical-asr-setup` | Stage 1 of Clinical ASR Flywheel. Use when bootstrapping a cycle: NVCF+MW disclosure, NVIDIA_API_KEY check, deps install, TTS+ASR smoke test. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/digital-health-clinical-asr-setup/SKILL.md) |
| `kermt-pretrain-scratch` | Pretrain a fresh KERMT model from scratch on a user-provided corpus. Builds a new vocabulary from the corpus, instantiates the model architecture from… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-kermt-pretrain-scratch/SKILL.md) |
| `kermt-setup` | Bootstrap the KERMT agent environment — verify host docker + nvidia-container-toolkit, build the kermt:latest image from the repo's Dockerfile if it d… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-kermt-setup/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/boltz2-nim"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

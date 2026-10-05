# 모델 학습·조정 / 설치·배포 / 1

[도메인으로](../domains/training.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `kermt-pretrain-scratch` | Pretrain a fresh KERMT model from scratch on a user-provided corpus. Builds a new vocabulary from the corpus, instantiates the model architecture from… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-kermt-pretrain-scratch/SKILL.md) |
| `kermt-setup` | Bootstrap the KERMT agent environment — verify host docker + nvidia-container-toolkit, build the kermt:latest image from the repo's Dockerfile if it d… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-kermt-setup/SKILL.md) |
| `launch-nemo-rl` | Playbook for launching, monitoring, stopping, and debugging NeMo-RL recipes on a Kubernetes cluster via the nrl-k8s CLI. Covers ephemeral vs long-live… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/launch-nemo-rl/SKILL.md) |
| `nemo-automodel-launcher-config` | Configure NeMo AutoModel job launches for interactive runs, Slurm clusters, and SkyPilot cloud execution. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-automodel-launcher-config/SKILL.md) |
| `nvflare-autofl` | Use for agent-assisted Auto-FL optimization of an existing NVFLARE job in simulation, POC, or production. Do not use for code conversion, diagnosis-on… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nvflare-autofl/SKILL.md) |
| `tao-launch-workflow` | The mandatory pre-launch gate and four-verb execution contract for every TAO workflow or action. Invoke BEFORE launching anything side-effecting — Aut… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-launch-workflow/SKILL.md) |
| `tao-setup` | One-time session setup and orchestration map for the TAO skill bank. Run this first when the TAO skills were installed individually (e.g. from a publi… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-setup/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/kermt-pretrain-scratch"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

# 배포·서빙·인프라 / 실행·사용 / 2

[도메인으로](../domains/infrastructure.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `tao-run-inference-service` | Start, query, and stop a network-specific TAO inference microservice ({network_arch}-inference-microservice) by delegating container execution to the … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-run-inference-service/SKILL.md) |
| `tao-run-on-brev` | Run a TAO training/evaluation/inference container on an NVIDIA Brev GPU instance. Instance provisioning (create/search/stop/delete/login) is delegated… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-run-on-brev/SKILL.md) |
| `tao-run-on-kubernetes` | Kubernetes execution platform — submits TAO container jobs as k8s Jobs with NVIDIA GPU scheduling; single-pod for one node, Indexed Jobs for multi-nod… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-run-on-kubernetes/SKILL.md) |
| `tao-run-on-slurm` | Remote SLURM GPU cluster execution over SSH with sbatch/srun, Pyxis/Enroot containers, and Lustre-backed results. Use when running TAO training/eval/i… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-run-on-slurm/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/tao-run-inference-service"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

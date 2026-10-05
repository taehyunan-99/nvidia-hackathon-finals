# 배포·서빙·인프라 / 성능·조정 / 1

[도메인으로](../domains/infrastructure.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `doca-flow-dpa-perf` | Use this skill when the user is invoking doca_flow_dpa_perf on DPA-capable hardware (ConnectX-7 minimum supported, ConnectX-8 recommended, or BlueFiel… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-flow-dpa-perf/SKILL.md) |
| `doca-flow-perf` | Use this skill when the user is measuring the host or DPU-CPU control-plane rate of a DOCA Flow pipeline with doca_flow_perf — picking a JSON policy f… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-flow-perf/SKILL.md) |
| `jetson-optimize-memory` | Reclaim DRAM by disabling unused subsystems across MB1 BCT, MB2 BCT, kernel reserved-memory, and SWIOTLB. Use for headless or no-camera Jetson deploym… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/jetson-optimize-memory/SKILL.md) |
| `molmim-nim` | Use this skill for MolMIM, NVIDIA's BioNeMo NIM microservice for small-molecule latent-space generation and optimization. Invoke for MolMIM, molecular… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-molmim-nim/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/doca-flow-dpa-perf"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

# 배포·서빙·인프라 / 탐색·선택 / 1

[도메인으로](../domains/infrastructure.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `doca-bench-extension` | Use this skill when the operator is authoring, building, loading, or debugging a custom doca-bench plug-in — a versioned shared library with DOCA_EXPE… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-bench-extension/SKILL.md) |
| `doca-pcc` | Use this skill when the user is doing hands-on host-side DOCA PCC work to load a CUSTOM Programmable Congestion Control algorithm onto a BlueField DPU… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-pcc/SKILL.md) |
| `doca-public-knowledge-map` | Use this skill when the user needs to locate authoritative information about NVIDIA DOCA without access to the source tree — finding the right docs.nv… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-public-knowledge-map/SKILL.md) |
| `doca-upgrade` | Use this skill when the user is contemplating a DOCA upgrade or downgrade — moving a host to a newer DOCA release, refreshing the BlueField BFB, bumpi… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-upgrade/SKILL.md) |
| `doca-urom` | Use this skill when the user is doing hands-on DOCA UROM library work from the host side — wiring doca-urom under an HPC / UCX / MPI stack to OFFLOAD … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-urom/SKILL.md) |
| `doca-version` | Use this skill when the user is doing DOCA version handling — detecting the installed release, validating the four-way match across pkg-config doca-co… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-version/SKILL.md) |
| `drug-discovery-pipeline` | NOTE: molecule and target inputs and your NGC_API_KEY are transmitted to external NVIDIA-hosted API endpoints on every call. Use local NIM containers … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-drug-discovery-pipeline/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/doca-bench-extension"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

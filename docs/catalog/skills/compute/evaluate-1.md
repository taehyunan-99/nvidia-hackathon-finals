# GPU 개발·고급 계산 / 검증·평가 / 1

[도메인으로](../domains/compute.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `cudaq-importing` | Use when porting circuits from another framework (e.g. Qiskit) into CUDA-Q kernels while preserving the source algorithm and validation fidelity. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/cudaq-importing/SKILL.md) |
| `g-assist-mcp-skill` | Use this skill to check or change this machine's NVIDIA display and GPU settings, such as resolution, refresh rate, V-Sync, G-SYNC, brightness, color,… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/g-assist-mcp-skill/SKILL.md) |
| `jetson-video-benchmark` | Use when measuring Jetson Video Codec SDK or PyNvVideoCodec encode/decode throughput, comparing presets or surfaces, testing codec-worker capacity wit… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/jetson-video-benchmark/SKILL.md) |
| `tilegym-adding-cutile-kernel` | Add a new cuTile GPU kernel operator to TileGym. Covers dispatch registration in ops.py, cuTile backend implementation, __init__.py exports, test crea… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tilegym-adding-cutile-kernel/SKILL.md) |
| `warp-eval` | Evaluate whether an existing hot path is a credible NVIDIA Warp candidate. Use for irregular or spatial queries, particle or geometry simulation, bran… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/warp-eval/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/cudaq-importing"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

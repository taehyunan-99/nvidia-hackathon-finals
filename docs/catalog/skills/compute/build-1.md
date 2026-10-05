# GPU 개발·고급 계산 / 구현·연결 / 1

[도메인으로](../domains/compute.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `hsb-ip-create-top` | Create or explain fixed-format HSB FPGA_top.sv wrappers from validated HOLOLINK_def.svh files. Do not use for def generation or validation. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/hsb-ip-create-top/SKILL.md) |
| `jetson-video-pipeline` | Use when planning, executing, and independently validating Jetson Video Codec SDK or PyNvVideoCodec encode/decode, transcode, segmentation, container … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/jetson-video-pipeline/SKILL.md) |
| `nvidia-app` | NVIDIA App MCP: drivers, games, laptops, overlay. Check drivers, manage and optimize games, configure laptop features. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nvidia-app/SKILL.md) |
| `tilegym-converting-cutile-to-julia` | Converts cuTile Python GPU kernels (@ct.kernel) to cuTile.jl Julia equivalents. Handles kernel syntax translation, 0-indexed to 1-indexed conversion, … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tilegym-converting-cutile-to-julia/SKILL.md) |
| `tilegym-converting-cutile-to-triton` | Converts cuTile GPU kernels (@ct.kernel) to Triton (@triton.jit). Handles standard in-repo conversion, debugging (cudaErrorIllegalAddress, shape misma… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tilegym-converting-cutile-to-triton/SKILL.md) |
| `tilegym-monkey-patch-kernels-to-transformers` | Integrate TileGym kernels into Hugging Face `transformers` models by replacing the library's submodule(s) and certain class(es)' implementations, and … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tilegym-monkey-patch-kernels-to-transformers/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/hsb-ip-create-top"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

# 로봇·물리·시뮬레이션 / 검증·평가 / 1

[도메인으로](../domains/robotics.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `hsb-ip-def` | Generate, validate, compare, or explain HSB HOLOLINK_def.svh macros. Do not use for FPGA_top.sv wrappers or packetizer-only derivation. Generation run… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/hsb-ip-def/SKILL.md) |
| `hsb-ip-packetizer` | Choose or explain HSB Sensor RX packetizer fields for HOLOLINK_def.svh. Do not use for full defs, validation, or runtime APB programming. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/hsb-ip-packetizer/SKILL.md) |
| `hsb-test` | Execute QA test plans on Holoscan Sensor Bridge hardware. Reads a user-provided test document, filters tests by the user's setup, determines which tes… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/hsb-test/SKILL.md) |
| `i4h-workflow-dataset-annotate` | Grade or filter workflow HDF5 episodes with an OpenAI-compatible vision model. Use for visual success labels; do not use for replay, policy evaluation… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/i4h-workflow-dataset-annotate/SKILL.md) |
| `i4h-workflow-dataset-replay` | Replay a workflow HDF5 episode through its original Scene. Use for visual trajectory and recording verification; do not use for policy evaluation or L… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/i4h-workflow-dataset-replay/SKILL.md) |
| `i4h-workflow-e2e` | Run the maintained workflow data-to-policy pipeline from recording through checkpoint validation. Use for full end-to-end requests; do not use for one… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/i4h-workflow-e2e/SKILL.md) |
| `i4h-workflow-train-rl` | Use when training, evaluating, or exporting Workflow policies with online RSL-RL or RLinf, including RL checkpoint and Workflow handoff. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/i4h-workflow-train-rl/SKILL.md) |
| `i4h-workflow-validate` | Run the root-level workflow runtime policy or rule-based rollouts and verify simulator success. Use for evaluation, checkpoints, or local controllers;… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/i4h-workflow-validate/SKILL.md) |
| `jetson-memory-audit` | Measure Jetson DRAM/NvMap usage and verify before/after memory reclamation with live audit data. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/jetson-memory-audit/SKILL.md) |
| `jetson-validate-image` | Use after jetson-flash-image to run static BSP checks, on-target smoke/regression tests on a flashed DUT, or both. Not for build or flash steps. Trigg… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/jetson-validate-image/SKILL.md) |
| `omniverse-cad-to-simready` | Coordinate the end-to-end CAD/source-asset to SimReady workflow. Use for broad requests such as CAD to SimReady, source asset to simulation-ready USD,… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/omniverse-cad-to-simready/SKILL.md) |
| `paidf-curation-and-retrieval` | Use when operating PAIDF Curation and Retrieval or NVIDIA Cosmos Curator pipelines (split, filter, caption, embed, dedup, shard, image annotate) or PA… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/paidf-curation-and-retrieval/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/hsb-ip-def"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

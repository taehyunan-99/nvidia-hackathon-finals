# 배포·서빙·인프라 / 검증·평가 / 1

[도메인으로](../domains/infrastructure.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `doca-aes-gcm` | Use this skill when the user is doing hands-on DOCA AES-GCM work on a BlueField DPU or ConnectX NIC — configuring `doca_aes_gcm_task_encrypt` / `_task… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-aes-gcm/SKILL.md) |
| `doca-bench` | Run `doca_bench` (DOCA 2.7.0 or newer) to measure throughput, bulk latency, precision latency, or maximum bandwidth for RDMA, Compress, AES-GCM, SHA, … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-bench/SKILL.md) |
| `doca-pcc-ztr-rttcc-algo` | Use this skill when the user is doing hands-on deployment, tuning, or evaluation of the DOCA-shipped Zero-Touch RoCE RTT-based Congestion Control (ZTR… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-pcc-ztr-rttcc-algo/SKILL.md) |
| `dynamo-interconnect-check` | Validate that a Dynamo deployment's NIXL/UCX/NCCL interconnect is ready for disaggregated serving over RDMA/NVLink. Use after recipe-runner brings a d… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/dynamo-interconnect-check/SKILL.md) |
| `jetson-llm-benchmark` | Benchmark Jetson LLM/VLM serving performance across vLLM, llama.cpp, and Ollama with structured JSON output. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/jetson-llm-benchmark/SKILL.md) |
| `tao-data-io` | The data-mover for TAO jobs — decides the storage tier (A pre-positioned mount with zero fetch / B volume-from-S3 / C ephemeral in-compute fetch), sta… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-data-io/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/doca-aes-gcm"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

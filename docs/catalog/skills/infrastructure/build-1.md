# 배포·서빙·인프라 / 구현·연결 / 1

[도메인으로](../domains/infrastructure.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `doca-argp` | Use this skill for hands-on DOCA Arg Parser CLI work on a shipped sample or new DOCA-using app — adding / removing / renaming flags; wiring `doca_argp… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-argp/SKILL.md) |
| `doca-dma` | Use this skill when the user is doing hands-on DOCA DMA programming — bringing up a doca_dma context, configuring the single doca_dma_task_memcpy task… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-dma/SKILL.md) |
| `doca-erasure-coding` | Use this skill when the user is doing hands-on DOCA Erasure Coding programming on a BlueField DPU, ConnectX NIC, or host — bringing up a doca_ec conte… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-erasure-coding/SKILL.md) |
| `doca-flow-dpa-provider` | Use this skill when the user is doing hands-on DOCA Flow DPA Provider work — exporting a `doca-flow` pipe or external resource (index-selector/memory)… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-flow-dpa-provider/SKILL.md) |
| `doca-flow-grpc-server` | PLAINTEXT-ONLY: the shipped `doca_flow_grpc` server uses `grpc::InsecureServerCredentials()` with NO TLS / mTLS / token-auth knob on the binary — tran… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-flow-grpc-server/SKILL.md) |
| `doca-gpunetio-ib-write-bw` | Use this skill when the user is building, running, or interpreting the doca/tools/gpunetio_ib_write_bw client+server benchmark — a CUDA kernel on the … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-gpunetio-ib-write-bw/SKILL.md) |
| `doca-gpunetio-ib-write-lat` | Use this skill when the user is measuring GPU-kernel-initiated RDMA WRITE latency through doca-gpunetio — building and running the `gpunetio_ib_write_… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-gpunetio-ib-write-lat/SKILL.md) |
| `doca-rdma` | Use this skill when the user is doing hands-on DOCA RDMA programming on a BlueField DPU, ConnectX NIC, or DOCA host — bringing up an RDMA context on a… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-rdma/SKILL.md) |
| `doca-sha-offload-engine` | Use this skill when wiring the DOCA SHA Offload Engine (an OpenSSL ENGINE) into an existing OpenSSL pipeline to offload one-shot SHA-1, SHA-256, or SH… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-sha-offload-engine/SKILL.md) |
| `doca-urom-svc` | Operate the DOCA UROM Service container on BlueField Arm for remote memory operations (puts, gets, atomics, collectives) enqueued by a paired host usi… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-urom-svc/SKILL.md) |
| `drug-discovery-pipeline` | NOTE: molecule and target inputs and your NGC_API_KEY are transmitted to external NVIDIA-hosted API endpoints on every call. Use local NIM containers … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-drug-discovery-pipeline/SKILL.md) |
| `kermt-embed` | Extract per-molecule embeddings from any encoder-bearing KERMT checkpoint. Use a local checkpoint or optionally download a pinned Hugging Face model b… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-kermt-embed/SKILL.md) |
| `msa-structure-prediction-pipeline` | NOTE: your protein sequence and the retrieved MSA alignment are transmitted to external NVIDIA-hosted APIs (health.api.nvidia.com) on every call. Use … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-msa-structure-prediction-pipeline/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/doca-argp"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

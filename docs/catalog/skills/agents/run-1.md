# 에이전트·평가·정책 / 실행·사용 / 1

[도메인으로](../domains/agent-workflows.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `data-designer` | Use when the user wants to create a dataset, generate synthetic data, or build a data generation pipeline. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/data-designer/SKILL.md) |
| `nat-mcp-and-serving` | Use when serving NeMo Agent Toolkit workflows, exposing workflows through FastAPI, configuring MCP clients or servers, or troubleshooting transport an… | [SKILL.md](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-mcp-and-serving/SKILL.md) |
| `nemo-relay-debug-runtime-integration` | Use this skill when NeMo Relay is installed or imported but application-side runtime behavior is missing or incorrect, including load failures, inacti… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-relay-debug-runtime-integration/SKILL.md) |
| `nemo-relay-instrument-calls` | Use this skill when an application owns tool or LLM/provider call sites and needs to wrap them with NeMo Relay scopes and managed execution APIs for l… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-relay-instrument-calls/SKILL.md) |
| `nemo-relay-instrument-context-isolation` | Use this skill when concurrent requests, async tasks, threads, workers, goroutines, or agents need independent NeMo Relay scope stacks and correct anc… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-relay-instrument-context-isolation/SKILL.md) |
| `nemo-relay-instrument-typed-wrappers` | Use this skill when adding NeMo Relay typed wrappers, domain types, or provider codecs while preserving JSON middleware semantics and caller-visible b… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-relay-instrument-typed-wrappers/SKILL.md) |
| `nemo-retriever` | Use when searching, extracting, ingesting, or querying a document collection with the NeMo Retriever 26.8.1 CLI, including local LanceDB indexes and d… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-retriever/SKILL.md) |
| `nemo-retriever-mcp` | Use when a task needs to search or add documents through NeMo Retriever MCP. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-retriever-mcp/SKILL.md) |
| `skill-card-generator` | Use only to generate or update a governance skill card for a specified existing agent skill directory. Do not use for explaining, listing, comparing, … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/skill-card-generator/SKILL.md) |
| `skill-evolution` | Use before creating, editing, or deciding whether to update any AI coding agent skill in this repository, including corrections to existing skill beha… | [SKILL.md](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/skill-evolution/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/data-designer"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

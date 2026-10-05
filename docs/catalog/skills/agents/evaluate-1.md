# 에이전트·평가·정책 / 검증·평가 / 1

[도메인으로](../domains/agent-workflows.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `nat-evaluation` | Use when designing, configuring, running, or troubleshooting NeMo Agent Toolkit evaluations, datasets, evaluator selection, ATIF surfaces, quality gat… | [SKILL.md](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-evaluation/SKILL.md) |
| `nat-path-checks` | Use when fixing NeMo Agent Toolkit documentation path-check failures, especially failed `ci/scripts/path_checks.py` output, slash-delimited text mista… | [SKILL.md](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-path-checks/SKILL.md) |
| `nat-telemetry` | Use when adding, configuring, or troubleshooting NeMo Agent Toolkit logging, tracing, telemetry exporters, OpenTelemetry, Langfuse, LangSmith, Weave, … | [SKILL.md](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-telemetry/SKILL.md) |
| `nat-tools-and-functions` | Use when authoring, registering, composing, or testing custom NeMo Agent Toolkit tools, functions, function groups, Python components, custom agents, … | [SKILL.md](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-tools-and-functions/SKILL.md) |
| `nemotron-policy-generator` | Generates BYO custom safety policies for NVIDIA Nemotron content-safety guardrails — Nemotron-Content-Safety-Reasoning-4B (text) and multimodal Nemotr… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemotron-policy-generator/SKILL.md) |
| `rag-eval` | Filesystem RAG benchmarks: corpus/, train.json, evaluate_rag.py (RAGAS quality). Not for prod monitoring, latency/throughput benchmarking (use rag-per… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/rag-eval/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/nemo-agent-toolkit/nat-evaluation"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

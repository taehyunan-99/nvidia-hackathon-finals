# 에이전트·평가·정책 / 성능·조정 / 1

[도메인으로](../domains/agent-workflows.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `nat-optimization` | Use when configuring or running NeMo Agent Toolkit optimization with `nat optimize`, including Optuna parameter tuning, prompt evolution, optimizer si… | [SKILL.md](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-optimization/SKILL.md) |
| `nemo-relay-plugin-adaptive-tuning` | Use this skill when baseline NeMo Relay instrumentation exists and the user wants to configure or evaluate adaptive plugin behavior, including telemet… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-relay-plugin-adaptive-tuning/SKILL.md) |
| `rag-perf` | Performance benchmarking for a deployed NVIDIA RAG Blueprint server: profiling pass + aiperf load test driven by a single YAML config. Not for accurac… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/rag-perf/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/nemo-agent-toolkit/nat-optimization"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

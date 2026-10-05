# 에이전트·평가·정책 / 탐색·선택 / 1

[도메인으로](../domains/agent-workflows.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `doca-argus` | Use this skill when the user is deploying or operating the DOCA Argus Service — the packaged BlueField-side runtime-security container that watches th… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-argus/SKILL.md) |
| `nat-agent-configuration` | Use when selecting, configuring, composing, or troubleshooting NeMo Agent Toolkit agents and control-flow components, including ReAct, tool-calling, R… | [SKILL.md](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-agent-configuration/SKILL.md) |
| `nat-user-rules` | Use first for general NVIDIA NeMo Agent Toolkit coding-agent behavior, task routing, naming conventions, component discovery rules, and cross-skill gu… | [SKILL.md](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-user-rules/SKILL.md) |
| `nemoclaw-user-guide` | Guides human users' AI agents to the NemoClaw docs MCP server and canonical Fern documentation in Markdown form. Use when users ask how to install, co… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemoclaw-user-guide/SKILL.md) |
| `nvidia-skill-finder` | Use for NVIDIA-related requests where an NVIDIA skill might help, even if the user did not ask for a skill. Trigger on NVIDIA products, hardware, soft… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nvidia-skill-finder/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/doca-argus"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

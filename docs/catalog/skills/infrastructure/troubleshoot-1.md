# 배포·서빙·인프라 / 문제 해결 / 1

[도메인으로](../domains/infrastructure.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `doca-debug` | Use this skill when the user is debugging any DOCA symptom — a build that won't compile, a link step that can't resolve a doca_* symbol, a runtime cal… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-debug/SKILL.md) |
| `doca-dpa-hl-tracer` | Use this skill when the user runs doca_dpa_hl_tracer to capture/decode DPA-side traces at the programming-events layer (kernel entry/exit, sync points… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-dpa-hl-tracer/SKILL.md) |
| `doca-pcc-counters` | Use this skill when the user is invoking the DOCA PCC Counters tool — the `pcc_counters.sh` bash script under the DOCA tools directory — to arm and re… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/doca-pcc-counters/SKILL.md) |
| `dynamo-troubleshoot` | Diagnose failed or unhealthy Dynamo deployments. Use when pods, model-cache jobs, PVCs, workers, frontend/router health, endpoints, or benchmark jobs … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/dynamo-troubleshoot/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/doca-debug"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

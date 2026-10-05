# 영상·이미지·비전 / 실행·사용 / 3

[도메인으로](../domains/vision.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `vss-ask-video` | Use this skill to ask the VSS agent's video_understanding tool a fresh visual question about a recorded clip. Not for prior tool output, search hits, … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-ask-video/SKILL.md) |
| `vss-generate-video-calibration` | Use to run AutoMagicCalib on local MP4s, RTSP, or the bundled sample dataset, and to deploy vss-auto-calibration when needed. Do not use for non-AMC c… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-generate-video-calibration/SKILL.md) |
| `vss-generate-video-report` | Use this skill when producing a VSS analysis report — Mode A per-clip VLM, Mode B incident-range via video-analytics. Not for standalone video summari… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-generate-video-report/SKILL.md) |
| `vss-manage-video-io-storage` | Use to call the VIOS REST API (sensor list, timelines, clip extraction, snapshots, add/delete sensors and streams). Not for VLM inference or search. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-manage-video-io-storage/SKILL.md) |
| `vss-query-analytics` | Use this skill when reading video-analytics metrics, incidents, alerts, and sensor data via the VA-MCP server (port 9901). Not for live VLM or inciden… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-query-analytics/SKILL.md) |
| `vss-search-archive` | Use this skill to run top-level VSS fusion search on archived video, or to ingest video files / RTSP streams for search. Do NOT use for ad-hoc visual … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-search-archive/SKILL.md) |
| `vss-setup-video-analytics-api` | Use to deploy the vss-video-analytics-api REST service standalone (config-source, data-log bind, Elasticsearch, optional Kafka). Not for full warehous… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-setup-video-analytics-api/SKILL.md) |
| `vss-summarize-video` | Use to summarize a recorded video via the LVS summarization microservice (HITL-gated) with a VLM fallback. Not for report generation or live RTSP capt… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-summarize-video/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/vss-ask-video"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

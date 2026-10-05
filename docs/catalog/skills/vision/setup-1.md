# 영상·이미지·비전 / 설치·배포 / 1

[도메인으로](../domains/vision.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `amc-setup-calibration-stack` | Launch AutoMagicCalib microservice and web UI from NGC release images via Docker Compose. Use when user says 'deploy auto calibration', 'launch auto c… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/amc-setup-calibration-stack/SKILL.md) |
| `nvidia-broadcast` | Use when controlling NVIDIA Broadcast through MCP to apply effects, process local media, select devices, or change camera resolution, or when Broadcas… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nvidia-broadcast/SKILL.md) |
| `tao-port-huggingface-model` | Integrate a HuggingFace Computer Vision model into the NVIDIA TAO Toolkit ecosystem (tao-core config, tao-pytorch trainer, tao-deploy TensorRT pipelin… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-port-huggingface-model/SKILL.md) |
| `vss-deploy-dense-captioning` | Use this skill when deploying standalone RT-VLM dense captioning or calling its REST API (uploads, captions, streams, chat-completions, Kafka). Not fo… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-deploy-dense-captioning/SKILL.md) |
| `vss-deploy-detection-tracking-2d` | Use this skill when the user wants to deploy, run, debug, tear down, or call the REST API of the RTVI-CV 2D detection / tracking microservice. Trigger… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-deploy-detection-tracking-2d/SKILL.md) |
| `vss-deploy-detection-tracking-3d` | Deploy and operate the RTVI-CV-3D microservice as MV3DT (`MODE=mv3dt`): per-camera DeepStream perception plus BEV Fusion over calibrated cameras. Supp… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-deploy-detection-tracking-3d/SKILL.md) |
| `vss-deploy-profile` | Use to select, configure, deploy, verify, debug, or tear down a VSS profile (base, search, lvs, warehouse, edge). Not for standalone microservices — u… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-deploy-profile/SKILL.md) |
| `vss-deploy-video-embedding` | Use this skill when deploying, operating, or integrating the VSS 3.2 GA RT-Embed Video Embedding microservice. Covers Docker Compose bring-up, GPU and… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-deploy-video-embedding/SKILL.md) |
| `vss-setup-behavior-analytics` | Use to deploy the vss-behavior-analytics service standalone (entrypoint, config-source, optional calibration). Not for the full warehouse deploy. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-setup-behavior-analytics/SKILL.md) |
| `vss-setup-video-analytics-api` | Use to deploy the vss-video-analytics-api REST service standalone (config-source, data-log bind, Elasticsearch, optional Kafka). Not for full warehous… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-setup-video-analytics-api/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/amc-setup-calibration-stack"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

# 영상·이미지·비전 / 구현·연결 / 1

[도메인으로](../domains/vision.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `deepstream-dev` | NVIDIA DeepStream SDK development with Python pyservicemaker API. Use when building video analytics pipelines, GStreamer-based video processing, Tenso… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/deepstream-dev/SKILL.md) |
| `deepstream-generate-pipeline` | Build DeepStream GStreamer pipelines interactively. Use when the user asks about pipelines for video/image inference, detection, tracking, or streamin… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/deepstream-generate-pipeline/SKILL.md) |
| `deepstream-import-vision-model` | Use this skill to bring a supported object-detection vision model from HuggingFace or NVIDIA NGC into an NVIDIA DeepStream pipeline with end-to-end au… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/deepstream-import-vision-model/SKILL.md) |
| `deepstream-profile-pipeline` | Profile a DeepStream pipeline with Nsight Systems and derive its configs from the measurement. Use when the user asks for an efficient, performant, or… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/deepstream-profile-pipeline/SKILL.md) |
| `deepstream-sop` | Use this skill when building, deploying, evaluating, debugging, or measuring latency for the DeepStream SOP Inference Microservice — a GPU-accelerated… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/deepstream-sop/SKILL.md) |
| `dicom-series-to-volume` | Used for converting one CT DICOM series folder to a HU NIfTI volume with affine evidence. Not for multi-frame DICOM or clinical use. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/dicom-series-to-volume/SKILL.md) |
| `rtvi-cv-customize-model` | How to swap the DeepStream CV detection model in the VSS Alerts Blueprint verification (2d_cv) mode - covers ONNX export, custom bbox parsers, compose… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/rtvi-cv-customize-model/SKILL.md) |
| `rtvi-cv-scaffold-vss-service` | Scaffold a standalone RTVI CV microservice that plugs into VSS Search and Alerts profiles via Kafka mdx-raw. The shipped scaffold script is a YOLO26 r… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/rtvi-cv-scaffold-vss-service/SKILL.md) |
| `vss-manage-alerts` | Use for VSS alert workflows — real-time monitoring, Alert-Bridge subscriptions, Slack notifications, incident queries, camera onboarding. Not for non-… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-manage-alerts/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/deepstream-dev"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

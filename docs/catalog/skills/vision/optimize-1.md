# 영상·이미지·비전 / 성능·조정 / 1

[도메인으로](../domains/vision.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `deepstream-profile-pipeline` | Profile a DeepStream pipeline with Nsight Systems and derive its configs from the measurement. Use when the user asks for an efficient, performant, or… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/deepstream-profile-pipeline/SKILL.md) |
| `nv-generate-mr-brain-finetune` | Used for finetuning NV-Generate-CTMR MR-Brain v1 for T1, T2, FLAIR, SWI, or MRA data from a NIfTI datalist. Not for clinical or production data approv… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nv-generate-mr-brain-finetune/SKILL.md) |
| `nv-generate-vae-finetune` | Used for finetuning the NV-Generate-CTMR MAISI VAE from CT/MRI NIfTI datalists. Not for clinical or production data approval. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nv-generate-vae-finetune/SKILL.md) |
| `nv-segment-ct-finetune` | Runs standard or fixed-channel softmax finetuning of NV-Segment-CT VISTA3D on CT NIfTI image/label datasets, with optional MONAI-native MLflow trackin… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nv-segment-ct-finetune/SKILL.md) |
| `tao-finetune-clip` | CLIP vision-language model for image-text retrieval, zero-shot classification, embedding extraction, ONNX export, and TensorRT deployment. Use when fi… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-finetune-clip/SKILL.md) |
| `tao-finetune-cosmos-embed` | Cosmos-Embed1 video-text embedding for text-to-video retrieval, video-to-video search, semantic deduplication, and fine-tuning. Use when the user asks… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-finetune-cosmos-embed/SKILL.md) |
| `tao-finetune-video-clip` | InternVideo2-CLIP L14 (TAO video_clip) for video-text retrieval, zero-shot classification, embedding extraction, LoRA fine-tuning, ONNX export, and Te… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-finetune-video-clip/SKILL.md) |
| `tao-train-image-classification` | PyTorch-based TAO image classification. Supports a wide range of backbones (FAN, EfficientNet, ResNet, etc.) with distillation and quantization for de… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-train-image-classification/SKILL.md) |
| `tao-train-rtdetr` | RT-DETR (Real-Time DEtection TRansformer) for 2D object detection. Designed for real-time inference with competitive accuracy and supports distillatio… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-train-rtdetr/SKILL.md) |
| `vss-deploy-profile` | Use to select, configure, deploy, verify, debug, or tear down a VSS profile (base, search, lvs, warehouse, edge). Not for standalone microservices — u… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-deploy-profile/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/deepstream-profile-pipeline"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

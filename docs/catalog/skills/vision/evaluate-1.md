# 영상·이미지·비전 / 검증·평가 / 1

[도메인으로](../domains/vision.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `nv-reason-cxr` | Used for command-shape or live NV-Reason-CXR chest X-ray reasoning smoke tests. Not for diagnosis or clinical reporting. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nv-reason-cxr/SKILL.md) |
| `rtvi-vlm-customize-model` | How to swap the VLM in the VSS Alerts Blueprint — covers RTVI-VLM microservice deployment methods, all three VLM consumers (rtvi-vlm, vlm-as-verifier,… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/rtvi-vlm-customize-model/SKILL.md) |
| `tao-analyze-changenet-rca` | Performs deep Root Cause Analysis (RCA) on NVIDIA TAO Visual ChangeNet classification experiments with image-evidence-driven investigation. Use when a… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-analyze-changenet-rca/SKILL.md) |
| `tao-analyze-gaps-visual-changenet` | Performs gap analysis on NVIDIA TAO VCN Classify (Visual Component Net) experiments by invoking the pinned TAO data-services container directly via `d… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-analyze-gaps-visual-changenet/SKILL.md) |
| `tao-train-optical-inspection` | Optical Inspection for defect detection using Siamese networks. Compares image pairs to detect manufacturing defects, anomalies, or quality issues. Us… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-train-optical-inspection/SKILL.md) |
| `tao-train-visual-changenet` | Visual ChangeNet for binary image classification and segmentation in AOI defect detection. Use when training, evaluating, exporting, or running infere… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-train-visual-changenet/SKILL.md) |
| `tao-validate-recipe-transfer` | Port a published computer vision paper's official code and training recipe onto a customer's own dataset, or diagnose why such a transfer produced bad… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-validate-recipe-transfer/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/nv-reason-cxr"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

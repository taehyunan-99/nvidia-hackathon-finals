# 생명과학·의료 / 구현·연결 / 1

[도메인으로](../domains/biology.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `dicom-series-to-volume` | Used for converting one CT DICOM series folder to a HU NIfTI volume with affine evidence. Not for multi-frame DICOM or clinical use. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/dicom-series-to-volume/SKILL.md) |
| `digital-health-clinical-asr-build` | Stage 2 of the Clinical ASR Flywheel. Use when curating clinical terms, tagging IPA, and synthesizing a NeMo manifest. NOT for scoring (use /digital-h… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/digital-health-clinical-asr-build/SKILL.md) |
| `drug-discovery-pipeline` | NOTE: molecule and target inputs and your NGC_API_KEY are transmitted to external NVIDIA-hosted API endpoints on every call. Use local NIM containers … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-drug-discovery-pipeline/SKILL.md) |
| `kermt-continue-pretrain` | Continue KERMT pretraining on a custom SMILES corpus with a grover_base, cmim, or hybrid checkpoint. Use a local checkpoint or optionally download a p… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-kermt-continue-pretrain/SKILL.md) |
| `kermt-embed` | Extract per-molecule embeddings from any encoder-bearing KERMT checkpoint. Use a local checkpoint or optionally download a pinned Hugging Face model b… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-kermt-embed/SKILL.md) |
| `msa-structure-prediction-pipeline` | NOTE: your protein sequence and the retrieved MSA alignment are transmitted to external NVIDIA-hosted APIs (health.api.nvidia.com) on every call. Use … | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-msa-structure-prediction-pipeline/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/dicom-series-to-volume"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

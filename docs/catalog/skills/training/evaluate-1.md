# 모델 학습·조정 / 검증·평가 / 1

[도메인으로](../domains/training.md)

| 스킬 | 사용 목적 | 고정 원문 |
|---|---|---|
| `kermt-add-cmim-pretrain` | Convert a grover_base checkpoint (encoder-only or encoder + vocab heads) into a hybrid checkpoint by adding a randomly-initialized cMIM decoder + late… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-kermt-add-cmim-pretrain/SKILL.md) |
| `mcore-testing` | Test system for Megatron-LM. Covers test layout, recipe YAML structure, adding and running unit and functional tests, golden values, marker filters, a… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/mcore-testing/SKILL.md) |
| `nemo-mbridge-mlm-bridge-training` | Run Megatron-LM (MLM) and Megatron Bridge training with mock or real data. Covers correlation testing, available recipes, and multi-GPU examples. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-mbridge-mlm-bridge-training/SKILL.md) |
| `nemotron-retrieval-recipes` | Use when planning, debugging, tuning, evaluating, exporting, or deploying public Nemotron `embed`/`rerank` retrieval recipes. | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemotron-retrieval-recipes/SKILL.md) |
| `nvflare-orient` | Route open-ended NVFLARE advice and only conversion requests whose preliminary source inspection reports unresolved or conflicting ownership; never lo… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nvflare-orient/SKILL.md) |
| `tao-artifacts` | The contract home for TAO's SDK-free execution pipeline — authoritative JSON Schemas for the four typed artifacts (spec-bundle, job-record, results_di… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-artifacts/SKILL.md) |
| `tao-train-metric-learning-recognition` | Metric-learning recognition (ml-recog) for fine-grained visual recognition. Learns embeddings for retrieval-based matching (e.g., retail product recog… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-train-metric-learning-recognition/SKILL.md) |
| `tao-train-single-step` | Standard single-step train/eval/export workflow for any TAO model. Use when training a TAO model on a dataset without iterative data augmentation, Aut… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-train-single-step/SKILL.md) |
| `tao-validate-dataset-format` | Run `tao-daft validate` to check NVIDIA TAO DAFT datasets for structure, schema, and cross-reference errors. Do not use for non-DAFT formats. Use when… | [SKILL.md](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/tao-validate-dataset-format/SKILL.md) |

설치/환경/실행 정보: `python3 scripts/lookup.py --show "skill:nvidia/skills/kermt-add-cmim-pretrain"` 형식으로 조회한다.
공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.

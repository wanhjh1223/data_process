# PHYSICS Dataset

## Overview

This repository contains the processed **PHYSICS** dataset, sourced from [HuggingFace - desimfj/PHYSICS](https://huggingface.co/datasets/desimfj/PHYSICS).

## Dataset Statistics

| Split | Processed Samples | Shards |
|-------|------------------|--------|
| test  | 2,000            | 1      |

**Total: 2,000 physics problems**

## Data Format

The dataset is provided in **JSONL** format with the following schema:

```json
{
  "id": "openclaw_00000001",
  "type": "pretrain",
  "text": "physics problem content..."
}
```

### Fields

- `id`: Global unique identifier
- `type`: Data type (e.g., `pretrain`)
- `text`: The training text content containing physics problems

## File Structure

```
processed/
└── physics_test_part_00000.jsonl.gz   # 2,000 physics problems (gzipped)
```

## Usage

To extract and use the dataset:

```bash
# Extract the gzipped file
gunzip processed/physics_test_part_00000.jsonl.gz

# Read the JSONL file
head -n 5 processed/physics_test_part_00000.jsonl
```

## Processing Pipeline

The dataset was processed according to the [Task Specification](task_spec.md) which includes:

- Downloading raw data from HuggingFace
- Cleaning and organizing text content
- Converting to standardized JSONL format
- Context length control (max 4096 tokens)
- Automatic sharding (max 100k records per shard)

## GitHub Release

The full processed dataset is available as a GitHub Release attachment:

- **Release Tag**: `physics-v1.0-test`
- **File**: `physics_test_part_00000.jsonl.gz`

## License

Please refer to the original dataset source for licensing information.

---

*Processed by OpenClaw Agent*

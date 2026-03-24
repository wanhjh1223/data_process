# MedQA Dataset

This repository contains the processed MedQA dataset from BigBio, ready for use in training and evaluation of medical QA models.

## Dataset Overview

- **Source**: [BigBio/MedQA](https://huggingface.co/datasets/bigbio/med_qa) on HuggingFace
- **Total Samples**: 61,097 medical question-answer pairs
- **Regions Covered**: US (United States), Mainland China, and Taiwan
- **Format**: JSONL (JSON Lines)
- **Type**: Instruction-tuning data

## Data Statistics

| Split | Samples | File |
|-------|---------|------|
| Train | 48,876 | `medqa_train_part_00000.jsonl.gz` |
| Validation | 6,109 | `medqa_validation_part_00000.jsonl.gz` |
| Test | 6,112 | `medqa_test_part_00000.jsonl.gz` |

## Data Format

Each line in the JSONL files contains a JSON object with the following structure:

```json
{
  "id": "openclaw_00000001",
  "type": "instruction",
  "text": "Question: [Question text]\n\nAnswer: [Answer text]"
}
```

### Fields

- `id` (string): Globally unique identifier for each sample
- `type` (string): Data type, always "instruction" for this dataset
- `text` (string): The question and answer formatted for instruction tuning

## Usage

### Downloading from GitHub Releases

This dataset is distributed via GitHub Releases. Each split is available as a separate release:

- **Train**: [medqa-v1.0-train](../../releases/tag/medqa-v1.0-train)
- **Validation**: [medqa-v1.0-validation](../../releases/tag/medqa-v1.0-validation)  
- **Test**: [medqa-v1.0-test](../../releases/tag/medqa-v1.0-test)

### Loading the Data

```python
import gzip
import json

# Load train data
with gzip.open('medqa_train_part_00000.jsonl.gz', 'rt', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        print(data['text'])
```

## Data Processing

The raw dataset was processed using the script in `scripts/process_medqa.py`, which:

1. Downloads the MedQA dataset from HuggingFace
2. Extracts question and answer pairs from three regional sources (US, Mainland China, Taiwan)
3. Formats them into instruction-tuning format
4. Generates unique IDs for each sample
5. Outputs as compressed JSONL files

### Running the Processing Script

```bash
pip install datasets tqdm
python scripts/process_medqa.py
```

## Citation

If you use this dataset in your research, please cite the original MedQA paper:

```bibtex
@inproceedings{jin2021disease,
  title={What Disease does this Patient Have? A Large-scale Open Domain Question Answering Dataset from Medical Exams},
  author={Jin, Di and Pan, Eileen and Oufattole, Nassim and Weng, Wei-Hung and Fang, Hanyi and Szolovits, Peter},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  volume={35},
  number={13},
  pages={11385--11393},
  year={2021}
}
```

## License

Please refer to the original dataset's license on [HuggingFace](https://huggingface.co/datasets/bigbio/med_qa).

## Repository Structure

```
.
├── scripts/
│   └── process_medqa.py      # Data processing script
├── examples/
│   └── examples.jsonl        # Sample data (100 records)
├── README.md                 # This file
└── task_spec.md              # Data processing specification
```

## Notes

- The dataset includes questions from medical licensing examinations across three regions
- Questions cover a wide range of medical topics and specialties
- Each question includes a correct answer choice
- The data is suitable for training medical QA models and instruction-tuning LLMs for medical domains

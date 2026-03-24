# MedMCQA Dataset Processing

MedMCQA 数据集处理版本

## 📊 数据说明

- **来源**: https://huggingface.co/datasets/openlifescienceai/medmcqa
- **规模**: 193,155 条
  - Train: 182,822 条
  - Validation: 4,183 条
  - Test: 6,150 条
- **任务类型**: 医学问答

## 📁 输出格式

标准 JSONL 格式，每行一个 JSON 对象：

```json
{"id": "openclaw_00000001", "type": "instruction", "text": "训练文本内容"}
```

## 📂 文件结构

```
medmcqa/
├── scripts/
│   └── process_medmcqa.py
├── examples/
│   └── examples.jsonl
├── processed/
│   ├── medmcqa_train_part_00000.jsonl.gz
│   ├── medmcqa_train_part_00001.jsonl.gz
│   ├── medmcqa_validation_part_00000.jsonl.gz
│   └── medmcqa_test_part_00000.jsonl.gz
├── task_spec.md
├── README.md
└── stats.json
```

## 📥 下载数据

完整数据集通过 GitHub Release 分发：

- **Train**: https://github.com/wanhjh1223/data_process/releases/tag/medmcqa-v1.0-train
- **Validation**: https://github.com/wanhjh1223/data_process/releases/tag/medmcqa-v1.0-validation
- **Test**: https://github.com/wanhjh1223/data_process/releases/tag/medmcqa-v1.0-test

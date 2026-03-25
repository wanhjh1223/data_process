# MedMCQA Dataset Processing

MedMCQA 数据集处理版本

## 📊 数据说明

- **来源**: https://huggingface.co/datasets/openlifescienceai/medmcqa
- **规模**: 约 163,000 条（仅 single choice）
  - Train: ~155,000 条
  - Validation: ~3,500 条
  - Test: ~5,100 条
- **任务类型**: 医学单选题问答

## 📝 数据处理说明

### 数据过滤
- **过滤条件**: 仅保留 `choice_type == 'single'` 的样本
- **原因**: multi choice 样本存在数据不一致性问题
- **过滤比例**: 约 15% 的原始数据被过滤

### 输出格式
标准 JSONL 格式，每行一个 JSON 对象：

```json
{"id": "openclaw_00000001", "type": "instruction", "text": "训练文本内容"}
```

文本格式示例：
```
There is a single choice question about medical. Answer the question by replying A, B, C or D.
Question: xxx

Option A: xxx
Option B: xxx
Option C: xxx
Option D: xxx
Answer: 
C

Explanation: xxx
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

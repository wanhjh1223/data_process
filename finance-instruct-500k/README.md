# Finance-Instruct-500k 数据集处理

## 数据来源

- **原始数据集**: Josephgflowers/Finance-Instruct-500k (HuggingFace)
- **实际使用**: Data-by-IngeniusAI/Finance-R1-Distill (ModelScope)
  - 这是 Finance-Instruct-500k 的 R1 蒸馏版本，包含高质量金融指令数据
- **本地路径**: `modelscope_data/Data-by-IngeniusAI/`

## 数据格式

原始数据格式：
```json
{
  "id": 1,
  "user_input": "解释财政政策和货币政策...",
  "reasoning_content": "详细推理过程...",
  "answer_r1": "最终答案...",
  "created_by": "Ingenius_AI"
}
```

处理后格式（标准 instruction 格式）：
```json
{
  "id": "openclaw_00000001",
  "type": "instruction",
  "text": "Instruction: 解释财政政策和货币政策...\n\nReasoning: 详细推理过程...\n\nOutput: 最终答案..."
}
```

## 处理统计

- **原始样本数**: 2,376
- **处理后样本数**: 2,341
- **跳过样本数**: 35 (内容过短或格式不完整)
- **分片数**: 1

## 输出文件

| 文件 | 大小 | 说明 |
|------|------|------|
| `finance_instruct_part_00000.jsonl.gz` | ~6.6 MB | 主数据集 (2,341 条) |
| `examples/examples.jsonl` | - | 示例数据 (100 条) |

## 数据特点

- **领域**: 金融、经济学
- **类型**: 指令微调数据
- **包含推理链**: 每个样本都有详细的 reasoning_content
- **高质量**: R1 蒸馏生成，逻辑严谨

## 使用方法

```python
import gzip
import json

with gzip.open("processed/finance_instruct_part_00000.jsonl.gz", "rt") as f:
    for line in f:
        data = json.loads(line)
        print(data["text"])
```

## GitHub Release

数据集发布在: https://github.com/wanhjh1223/data_process/releases
- Tag: `finance-instruct-v1.0`

## 许可证

遵循原始数据集许可证。

---
*处理时间: 2026-03-25*

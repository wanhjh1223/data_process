# 法务问答数据集

## 数据来源
- **原始项目**: [CrimeKgAssitant](https://github.com/liuhuanyong/CrimeKgAssitant)
- **作者**: 刘焕勇
- **许可证**: 遵循原项目许可

## 数据说明

| 字段 | 说明 |
|------|------|
| `question` | 法律问题 |
| `answer` | 法律回答 |
| `text` | 问题+回答的完整文本 |

## 数据量
- **总记录**: 203,459条问答对
- **文件**: 
  - legal_qa_part_001.jsonl (100,000条)
  - legal_qa_part_002.jsonl (100,000条)
  - legal_qa_part_003.jsonl (3,459条)
- **格式**: JSONL

## 处理脚本
- `process_legal_qa.py` - 处理原始数据生成 JSONL

## 使用示例

```python
import json

with open("legal_qa_part_001.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        print(record["question"])  # 问题
        print(record["answer"])    # 回答
```

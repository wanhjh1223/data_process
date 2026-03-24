# 罪名知识图谱数据集

## 数据来源
- **原始项目**: [CrimeKgAssitant](https://github.com/liuhuanyong/CrimeKgAssitant)
- **作者**: 刘焕勇
- **许可证**: 遵循原项目许可

## 数据说明

| 字段 | 说明 |
|------|------|
| `crime_big` | 罪名大类（如：危害国家安全罪） |
| `crime_small` | 具体罪名（如：背叛国家罪） |
| `gainian` | 罪名概念 |
| `tezheng` | 构成要件 |
| `rending` | 认定标准 |
| `chufa` | 处罚规定 |
| `fatiao` | 相关法条 |
| `jieshi` | 司法解释 |
| `bianhu` | 辩护要点 |

## 数据量
- **总记录**: 856条罪名知识
- **文件**: crime_kg_part_001.jsonl
- **格式**: JSONL

## 处理脚本
- `process_crime_kg.py` - 处理原始数据生成 JSONL

## 使用示例

```python
import json

with open("crime_kg_part_001.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        print(record["crime_small"])  # 具体罪名
        print(record["text"])         # 完整知识文本
```

# 法律法规数据集

## 数据来源
- **原始项目**: [LawRefBook/Laws](https://github.com/LawRefBook/Laws)
- **许可证**: 遵循原项目许可

## 数据说明

| 字段 | 说明 |
|------|------|
| `title` | 法律/司法解释名称 |
| `text` | 完整法律文本（含标题） |
| `category` | 分类（如：司法解释、法律） |
| `file_path` | 原始文件路径 |

## 数据量
- **总记录**: 3,531条法律法规
- **文件**: law_regulation_part_001.jsonl
- **格式**: JSONL

## 包含内容
- 宪法
- 刑法
- 民法典
- 行政法
- 经济法
- 最高人民法院/最高人民检察院司法解释

## 处理脚本
- `process_law_regulation.py` - 处理原始数据生成 JSONL

## 使用示例

```python
import json

with open("law_regulation_part_001.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        print(record["title"])   # 法律名称
        print(record["text"])    # 完整法律文本
```

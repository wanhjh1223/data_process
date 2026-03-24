# MoralExceptQA Dataset Processing

MoralExceptQA 数据集处理版本

## 📊 数据说明

- **来源**: https://huggingface.co/datasets/feradauto/MoralExceptQA
- **规模**: 148 条
- **任务类型**: 道德推理问答

## 📁 输出格式

标准 JSONL 格式，每行一个 JSON 对象：

```json
{"id": "openclaw_00000001", "type": "instruction", "text": "训练文本内容"}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 全局唯一ID，格式 `openclaw_{8位数字}` |
| `type` | string | 数据类型：`instruction` |
| `text` | string | 训练文本（场景+问题+选项+答案） |

## 📂 文件结构

```
moralexceptqa/
├── scripts/
│   └── process_moralexceptqa.py    # 数据处理脚本
├── examples/                        # 示例数据（≤100条）
│   └── examples.jsonl
├── processed/                       # 完整数据
│   └── moralexceptqa_part_00000.jsonl.gz
├── task_spec.md                     # 任务规范
├── README.md                        # 本文件
└── stats.json                       # 处理统计
```

## 📥 下载数据

完整数据集通过 GitHub Release 分发：

- **Release**: https://github.com/wanhjh1223/data_process/releases/tag/moralexceptqa-v1.0

## 🚀 使用方法

```python
import gzip
import json

# 加载压缩数据
with gzip.open("moralexceptqa_part_00000.jsonl.gz", "rt", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        print(data["id"], data["text"][:100])
```

## 📈 处理统计

| 指标 | 数值 |
|------|------|
| 原始样本数 | 148 |
| 处理后样本数 | 148 |
| 生成 Shard 数 | 1 |

## 🔧 重新处理

```bash
python scripts/process_moralexceptqa.py
```

# CaseHOLD Dataset Processing

CaseHOLD (Case Holdings on Legal Decisions) 法律预训练数据集处理版本

## 📊 数据说明

- **来源**: Harvard Law Library case law corpus (1965-present)
- **原始规模**: 训练集 45,000 / 验证集 3,900
- **任务类型**: 多选题问答 (Multiple Choice QA)

## 📁 输出格式

标准 JSONL 格式，每行一个 JSON 对象：

```json
{"id": "openclaw_00000001", "type": "pretrain", "text": "训练文本内容"}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 全局唯一ID，格式 `openclaw_{8位数字}` |
| `type` | string | 数据类型：`pretrain` |
| `text` | string | 训练文本（案例引用 + 正确holding） |

## 📂 文件结构

```
casehold_processed/
├── scripts/
│   └── process_casehold.py    # 数据处理脚本
├── examples/                   # 示例数据（≤100条）
│   ├── train_examples.jsonl
│   └── validation_examples.jsonl
├── processed/                  # 完整数据（不上传到repo）
│   ├── train_part_00000.jsonl.gz
│   └── validation_part_00000.jsonl.gz
├── task_spec.md               # 任务规范
└── README.md                  # 本文件
```

## 📥 下载数据

完整数据集通过 GitHub Release 分发：

- **Train**: https://github.com/wanhjh1223/data_process/releases/tag/casehold-v1.0-train
- **Validation**: https://github.com/wanhjh1223/data_process/releases/tag/casehold-v1.0-validation

## 🚀 使用方法

```python
import gzip
import json

# 加载压缩数据
with gzip.open('train_part_00000.jsonl.gz', 'rt', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        print(data['id'], data['text'][:100])
```

## 📈 处理统计

| 划分 | 原始样本 | 处理后样本 | Shard数 |
|------|----------|------------|---------|
| Train | 45,000 | 45,000 | 1 |
| Validation | 3,900 | 3,900 | 1 |

## 🔧 重新处理

```bash
python scripts/process_casehold.py
```

## 📚 引用

```bibtex
@inproceedings{zheng2021casehold,
  title={When Does Pretraining Help? Assessing Self-Supervised Learning for Law and the CaseHOLD Dataset},
  author={Zheng, Lucille and Guha, Neel and Anderson, Brandon and Henderson, Peter and Ho, Daniel E},
  booktitle={ICAIL},
  year={2021}
}
```

# Moral Stories 数据集处理

道德故事数据集处理项目，基于 [demelin/moral_stories](https://huggingface.co/datasets/demelin/moral_stories)。

## 📊 数据说明

| 属性 | 值 |
|------|-----|
| 原始数据源 | HuggingFace: demelin/moral_stories |
| 处理后样本数 | 12,000 |
| 字段格式 | ID, norm, situation, intention, moral_action, moral_consequence, immoral_action, immoral_consequence |
| 输出格式 | JSONL (id, text, type) |
| 最大上下文长度 | 4096 字符 |

## 📋 数据结构

原始数据包含以下字段：

| 字段 | 说明 |
|------|------|
| `ID` | 样本唯一标识 |
| `norm` | 道德规范 (如 "It's responsible to keep children safe.") |
| `situation` | 情境描述 |
| `intention` | 行为意图 |
| `moral_action` | 道德行为 |
| `moral_consequence` | 道德后果 |
| `immoral_action` | 不道德行为 |
| `immoral_consequence` | 不道德后果 |

## 🔧 使用方法

```bash
# 安装依赖
pip install tqdm

# 下载原始数据
curl -L -o moral_stories_full.jsonl \
  "https://huggingface.co/datasets/demelin/moral_stories/resolve/main/data/moral_stories_full.jsonl"

# 处理数据
python3 process_moral_stories.py

# 输出目录
processed_data/
└── moral_stories_part_001.jsonl
```

## 📁 输出格式

```json
{
  "id": "openclaw_37TD41K0AI7TYQGNUFTSCYCNT25SCN",
  "text": "【道德规范】It's responsible to keep children safe.\n【情境】Kent was watching his kids...\n【意图】Kent wants to add security...\n【道德行为】Kent installs cameras...\n【道德后果】Kent's kids feel much safer...\n【不道德行为】Kent installs an electric fence...\n【不道德后果】One of Kent's kids gets shocked...",
  "type": "moral_stories"
}
```

## 📦 完整数据下载

**Release:** [v1.0-moral-stories](https://github.com/wanhjh1223/data_process/releases/tag/v1.0-moral-stories)

- `moral_stories_part_001.jsonl` (8.08 MB, 12,000 条)

## 📊 处理统计

```
原始样本数: 12,000
处理后样本数: 12,000
跳过样本: 0
生成Shard: 1
平均文本长度: ~600 字符
```

## 📄 文件说明

- `process_moral_stories.py` - 数据处理脚本
- `moral_stories_full.jsonl` - 原始数据（需自行下载）
- `processed_data/` - 处理后输出数据

## 📝 更新记录

- **2026-03-23**: 初始版本，处理 12,000 条道德故事数据

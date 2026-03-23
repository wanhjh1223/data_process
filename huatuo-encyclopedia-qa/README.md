# Huatuo Encyclopedia QA 数据集处理

医学百科问答数据集处理项目，基于 [FreedomIntelligence/huatuo_encyclopedia_qa](https://huggingface.co/datasets/FreedomIntelligence/huatuo_encyclopedia_qa)。

## 📊 数据说明

| 属性 | 值 |
|------|-----|
| 原始数据源 | HuggingFace: FreedomIntelligence/huatuo_encyclopedia_qa |
| 处理后样本数 | 1,999 |
| 字段格式 | questions (list), answers (list) |
| 输出格式 | JSONL (id, text, type) |
| 最大上下文长度 | 4096 字符 |
| 单文件最大条数 | 100,000 |

## 🔧 使用方法

```bash
# 安装依赖
pip install tqdm

# 下载数据并处理
python3 scripts/process_local.py

# 输出目录
processed_data/
└── huatuo_part_001.jsonl
```

## 📁 输出格式

```json
{
  "id": "openclaw_00000001",
  "text": "问题：xxx\n回答：xxx",
  "type": "medical_encyclopedia"
}
```

## 📦 完整数据下载

完整处理后数据见 [GitHub Release v1.0-dataset](https://github.com/wanhjh1223/data_process/releases/tag/v1.0-dataset-huatuo)

## 📄 文件说明

- `scripts/process_local.py` - 数据处理脚本
- `examples/sample.jsonl` - 示例数据（100条）
- `processed_data/` - 完整输出数据

## 📊 处理统计

```
原始样本数: 2,000
处理后样本数: 1,999
跳过样本: 1 (过短文本)
生成Shard: 1
平均文本长度: ~1700 字符
```

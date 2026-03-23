# Huatuo Encyclopedia QA 数据集处理

医学百科问答数据集处理项目，基于 [FreedomIntelligence/huatuo_encyclopedia_qa](https://huggingface.co/datasets/FreedomIntelligence/huatuo_encyclopedia_qa)。

## 📊 数据说明

| 属性 | 值 |
|------|-----|
| 原始数据源 | HuggingFace: FreedomIntelligence/huatuo_encyclopedia_qa |
| 处理后样本数 | 364,328 (train: 362,329 / test: 1,000 / validation: 999) |
| 字段格式 | questions (list), answers (list) |
| 输出格式 | JSONL (id, text, type) |
| 最大上下文长度 | 4096 字符 |
| 单文件最大条数 | 100,000 |

## 🔧 使用方法

```bash
# 安装依赖
pip install datasets tqdm

# 流式加载并处理（推荐）
python3 process_stream.py

# 输出目录
processed_data/
├── huatuo_train_part_001.jsonl
├── huatuo_train_part_002.jsonl
├── huatuo_train_part_003.jsonl
├── huatuo_train_part_004.jsonl
├── huatuo_test_part_001.jsonl
└── huatuo_validation_part_001.jsonl
```

## 📁 输出格式

```json
{
  "id": "openclaw_train_00000001",
  "text": "问题：xxx\n回答：xxx",
  "type": "medical_encyclopedia"
}
```

## 📦 完整数据下载

**⚠️ 注意：数据集已按 train/test/validation 拆分为 3 个独立 Release！**

| Release | 数据集 | 样本数 | 文件数 | 下载链接 |
|---------|--------|--------|--------|----------|
| **v1.0-train** | 训练集 | 362,329 | 4 | [下载](https://github.com/wanhjh1223/data_process/releases/tag/v1.0-train) |
| **v1.0-test** | 测试集 | 1,000 | 1 | [下载](https://github.com/wanhjh1223/data_process/releases/tag/v1.0-test) |
| **v1.0-validation** | 验证集 | 999 | 1 | [下载](https://github.com/wanhjh1223/data_process/releases/tag/v1.0-validation) |

### 各 Release 文件详情

**v1.0-train:**
- `huatuo_train_part_001.jsonl` (100,000条, 163MB)
- `huatuo_train_part_002.jsonl` (100,000条, 164MB)
- `huatuo_train_part_003.jsonl` (100,000条, 165MB)
- `huatuo_train_part_004.jsonl` (62,329条, 103MB)

**v1.0-test:**
- `huatuo_test_part_001.jsonl` (1,000条, 1.7MB)

**v1.0-validation:**
- `huatuo_validation_part_001.jsonl` (999条, 1.7MB)

## 📄 文件说明

- `process_stream.py` - 流式数据处理脚本（推荐）
- `process_full.py` - 完整下载后处理脚本
- `examples/sample.jsonl` - 示例数据（100条）
- `processed_data/` - 完整输出数据
- `DATASET.md` - 详细数据文档

## 📊 处理统计

```
原始样本数:
  - train: 362,329
  - test: 1,000
  - validation: 1,000

处理后样本数:
  - train: 362,329
  - test: 1,000
  - validation: 999

生成Shard: 6 (train×4, test×1, validation×1)
```

## 📝 更新记录

- **2026-03-23**: 完整处理 train/test/validation，拆分为 3 个独立 Release

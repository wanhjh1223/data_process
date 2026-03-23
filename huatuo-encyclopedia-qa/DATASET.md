# Huatuo Encyclopedia QA 数据处理说明

## 📊 数据集来源
- **来源**: [FreedomIntelligence/huatuo_encyclopedia_qa](https://huggingface.co/datasets/FreedomIntelligence/huatuo_encyclopedia_qa)
- **镜像**: https://hf-mirror.com (国内加速)

## 📁 数据划分

数据集包含三个子集：

| 子集 | 文件名 | 预估大小 | 用途 |
|------|--------|----------|------|
| **训练集** | `train_datasets.jsonl` | ~576 MB | 模型训练 |
| **测试集** | `test_datasets.jsonl` | ~1.7 MB | 模型测试 |
| **验证集** | `validation_datasets.jsonl` | ~1.6 MB | 模型验证 |

## 📦 GitHub Release 发布计划

每个子集独立发布：

| Release 标签 | 对应数据 | 说明 |
|--------------|----------|------|
| `v1.0-train` | 训练集处理后数据 | 完整训练数据 |
| `v1.0-test` | 测试集处理后数据 | 完整测试数据 |
| `v1.0-validation` | 验证集处理后数据 | 完整验证数据 |

## 📐 输出格式

```json
{
  "id": "openclaw_00000001",
  "text": "问题：xxx\n回答：xxx",
  "type": "medical_encyclopedia"
}
```

## 🔧 处理参数

- **最大上下文长度**: 4096 字符
- **单文件最大条数**: 100,000
- **格式**: JSONL
- **跳过规则**: 少于20字符的短文本

## 📝 更新记录

- **2026-03-23**: 初始版本，分别处理 train/test/validation 三个子集

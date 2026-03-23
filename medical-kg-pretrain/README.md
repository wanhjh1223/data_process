# Medical Knowledge Graph Preprocessing for Pre-training

本项目用于处理 FreedomIntelligence/huatuo_knowledge_graph_qa 医学知识图谱数据集，将其转换为适合预训练的jsonl格式。

## 数据集信息

- **来源**: FreedomIntelligence/huatuo_knowledge_graph_qa
- **规模**: 798,444 条数据
- **类型**: 医学知识图谱问答数据

## 处理参数

- **最大上下文长度**: 4096 tokens
- **输出格式**: jsonl
- **单文件最大条数**: 100,000 条
- **字段**: `id`, `text`, `type`

## 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行处理脚本

```bash
python process_medical_data.py
```

## 输出文件

处理后的数据将保存在 `processed_data/` 目录下，文件命名格式：
- `medical_data_part_001.jsonl`
- `medical_data_part_002.jsonl`
- ...

## 数据结构

```json
{
  "id": 0,
  "text": "问题：xxx\n回答：xxx",
  "type": "medical_kg"
}
```

## 数据下载

### 从 Releases 下载（推荐）

处理后的完整数据已上传至 GitHub Releases：

📦 **[medical_data_v1.0.tar.gz](https://github.com/wanhjh1223/medical-kg-pretrain/releases/download/v1.0/medical_data_v1.0.tar.gz)** (48MB 压缩包)

- 总记录数：**796,444 条**
- 解压后大小：约 164MB
- 包含 8 个 jsonl 文件

```bash
# 下载并解压
wget https://github.com/wanhjh1223/medical-kg-pretrain/releases/download/v1.0/medical_data_v1.0.tar.gz
tar -xzf medical_data_v1.0.tar.gz
```

### 自行生成

如果数据有更新或需要自定义参数，可运行脚本：

```bash
python process_medical_data.py
```

处理后的文件结构：

| 文件 | 条数 | 大小 |
|------|------|------|
| medical_data_part_001.jsonl | 100,000 | ~21MB |
| medical_data_part_002.jsonl | 100,000 | ~21MB |
| ... | ... | ... |
| medical_data_part_008.jsonl | 96,444 | ~20MB |

## 数据示例

见 [sample_data.json](sample_data.json)（前 100 条示例）

## 许可证

数据原始许可证遵循 FreedomIntelligence/huatuo_knowledge_graph_qa

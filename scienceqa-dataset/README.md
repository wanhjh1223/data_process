# ScienceQA Dataset Processor

## 数据集信息

- **名称**: derek-thomas/ScienceQA
- **替代来源**: 原数据集 justsomerandomdude264/ScienceQA-Dataset 因 trust_remote_code 限制无法加载，改用 derek-thomas/ScienceQA
- **来源**: HuggingFace Datasets
- **类型**: 多模态科学问答数据集

## 处理规范

按照 `TASK_SPEC.md` 要求进行数据处理：

### 输出格式 (JSONL)
```json
{"id":"openclaw_00000001","type":"instruction","text":"【学科】Natural Sciences\n\n【主题】Biology\n\n【年级】Grade 5\n\n【知识点】光合作用的基本原理...\n\n【问题】植物如何利用阳光？\n\n【选项】\nA. 通过光合作用\nB. 通过吸收土壤养分\nC. 通过呼吸作用\nD. 通过蒸腾作用\n\n【解析】植物通过叶绿体中的光合作用将光能转化为化学能...\n\n【答案】A"}
```

### 字段映射

| 原始字段 | 输出字段 | 说明 |
|---------|---------|------|
| question | 【问题】 | 问题内容 |
| choices | 【选项】 | 选择题选项列表 |
| answer | 【答案】 | 正确答案 |
| rationale | 【解析】 | 解答解析 |
| lecture | 【知识点】 | 相关知识点讲解 |
| subject | 【学科】 | 学科分类 |
| topic | 【主题】 | 主题分类 |
| grade | 【年级】 | 适用年级 |

### 数据类型
- `type`: "instruction" (问答格式归类为指令类型)

## 使用方法

```bash
cd /root/.openclaw/workspace/data_process/scienceqa-dataset
python3 scripts/process_scienceqa.py
```

## 输出目录

- `output/` - 完整处理后的数据（按split分shard存储）
- `examples/` - 示例数据（最多100条）

## 数据切分规则

- 最大token数: 4096 (使用gpt2 tokenizer)
- 每个shard最大: 100,000条记录
- 超长文本自动按句子边界切分

## GitHub Release 上传

按不同split分别创建Release:
- `v1.0-train` - 训练集
- `v1.0-validation` - 验证集
- `v1.0-test` - 测试集

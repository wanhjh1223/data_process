# CaseHOLD Pretraining Dataset

CaseHOLD (Case Holdings on Legal Decisions) 法律预训练数据集处理版本

## 📊 数据说明

CaseHOLD 是 **LexGLUE** 基准测试中的法律多选题问答数据集，包含超过 53,000 条美国法院判决的裁决要点识别任务。

| 属性 | 说明 |
|------|------|
| **来源** | Harvard Law Library case law corpus (1965-present) |
| **原始规模** | 训练集 45,000 / 验证集 3,900 / 测试集 3,900 |
| **任务类型** | 多选题问答 (Multiple Choice QA) |
| **核心任务** | 根据案例引用识别正确的法律裁决要点 (holding) |

## 📁 文件结构

```
casehold_processed/
├── README.md                          # 本文件
├── train_triplet.jsonl               # 训练集 - 三联体格式
├── validation_triplet.jsonl          # 验证集 - 三联体格式
├── train_instruction.jsonl           # 训练集 - 指令格式
├── validation_instruction.jsonl      # 验证集 - 指令格式
├── train_contrastive.jsonl           # 训练集 - 对比学习格式
├── validation_contrastive.jsonl      # 验证集 - 对比学习格式
└── scripts/
    └── process_casehold.py           # 数据处理脚本
```

## 🔗 数据格式

### 1. 三联体格式 (Triplet) - 推荐用于法律领域预训练

```json
{
  "case_citation": "案例引用文本（不含holding）",
  "holding": "正确的法律裁决要点",
  "explanation": "解释说明",
  "legal_principle": "涉及的法律原则",
  "distractors": ["干扰项1", "干扰项2", "干扰项3", "干扰项4"],
  "full_text": "完整文本（holding已填充）"
}
```

**用途**: 构建"案例-裁决-解释"结构，符合法律领域预训练的最佳实践

### 2. 指令格式 (Instruction) - 用于 SFT 微调

```json
{
  "instruction": "根据以下法院判决引用，确定正确的法律裁决要点：",
  "input": "案例文本 + 5个选项",
  "output": "正确答案是：A. xxx",
  "label": 0,
  "choices": ["选项A", "选项B", "选项C", "选项D", "选项E"]
}
```

**用途**: 指令微调 (Supervised Fine-Tuning)

### 3. 对比学习格式 (Contrastive) - 用于检索模型

```json
{
  "anchor": "案例引用（查询）",
  "positive": "正确的holding（正样本）",
  "hard_negatives": ["错误选项1", "错误选项2", "错误选项3", "错误选项4"],
  "full_context": "完整上下文"
}
```

**用途**: 
- 训练法律文档 Embedding 模型
- RAG 检索系统训练
- **注意**: CaseHOLD 的干扰项是高质量难负样本！

## 🚀 快速开始

### 加载数据

```python
import json

# 加载三联体格式
with open("train_triplet.jsonl", "r") as f:
    triplets = [json.loads(line) for line in f]

# 加载指令格式
with open("train_instruction.jsonl", "r") as f:
    instructions = [json.loads(line) for line in f]
```

### 使用 Datasets 库

```python
from datasets import load_dataset

# 加载 JSONL 文件
dataset = load_dataset("json", data_files="train_triplet.jsonl")
```

## 💡 使用建议

### 场景1: 法律领域继续预训练
```python
# 数据混合比例建议
- FineWeb-Edu (通用): 70%
- 法律语料 (Legal-BERT等): 20%
- CaseHOLD 三联体: 10%

# 使用格式: train_triplet.jsonl 中的 full_text 字段
```

### 场景2: 法律指令微调 (SFT)
```python
# 直接使用指令格式
# train_instruction.jsonl + validation_instruction.jsonl
```

### 场景3: 法律检索系统 (RAG)
```python
# 使用对比学习格式
# anchor 作为 query
# positive 作为 target document
# hard_negatives 作为难负样本
```

### 场景4: 法考推理能力训练
```python
# 基于三联体格式合成 Chain-of-Thought 数据
# 构建"案例 → 分析 → 结论"推理链
```

## 📈 数据特点

1. **高质量难负样本**: 4 个干扰项都是语义相似的真实 holding，不是随机生成的
2. **时间划分**: 按时间顺序划分 train/dev/test，避免数据泄漏
3. **法律专业性**: 涉及美国各级法院判决，覆盖多个法律领域
4. **适合多种任务**: 分类、检索、生成、推理

## ⚠️ 注意事项

1. **测试集隔离**: 测试集 (3,900条) 未包含在本处理版本中，仅用于最终评估
2. **仅用于研究**: 本数据集仅供学术研究使用
3. **建议混合使用**: 单独使用 CaseHOLD 规模较小，建议与其他法律语料混合

## 🔧 重新处理数据

如果需要重新处理原始数据：

```bash
# 安装依赖
pip install datasets

# 运行处理脚本
python scripts/process_casehold.py
```

## 📚 相关数据集

- **LexGLUE**: https://huggingface.co/datasets/lex_glue
- **Legal-BERT**: https://huggingface.co/nlpaueb/legal-bert-base-uncased
- **LEDGAR**: 合同条款分类数据集
- **SCOTUS**: 美国最高法院判决数据集

## 📖 引用

如果您使用了本数据集，请引用：

```bibtex
@inproceedings{zheng2021casehold,
  title={When Does Pretraining Help? Assessing Self-Supervised Learning for Law and the CaseHOLD Dataset of 53,000+ Legal Holdings},
  author={Zheng, Lucille and Guha, Neel and Anderson, Brandon and Henderson, Peter and Ho, Daniel E},
  booktitle={Proceedings of the Eighteenth International Conference on Artificial Intelligence and Law},
  pages={159--168},
  year={2021}
}

@inproceedings{chalkidis2022lexglue,
  title={LexGLUE: A Benchmark Dataset for Legal Language Understanding in English},
  author={Chalkidis, Ilias and Fergadiotis, Manos and Malakasiotis, Prodromos and Aletras, Nikolaos and Androutsopoulos, Ion},
  booktitle={Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics},
  pages={4310--4329},
  year={2022}
}
```

## 📄 许可证

原始 CaseHOLD 数据集遵循原论文的许可证。本处理版本仅改变数据格式，不修改原始内容。

---

**最后更新**: 2026-03-24

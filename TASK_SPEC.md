# 数据处理 Agent 任务规范

> 版本: 1.0
> 创建时间: 2026-03-23
> 用途: 数据集自动处理标准化流程

---

## 🎯 任务目标

给定一个或多个数据集链接（GitHub / HuggingFace / 原始文件URL），Agent需要自动完成以下工作：

1. 下载或流式读取原始数据集
2. 清洗并组织文本内容
3. 控制上下文长度
4. 转换为符合规范的 JSONL 数据
5. 将处理脚本与样例上传至 GitHub 仓库
6. 将完整处理后的数据以 GitHub Release 附件形式上传

---

## 📥 输入

Agent会收到：
- 一个或多个数据集URL
- 示例：
  - `https://huggingface.co/datasets/xxx/yyy`
  - `https://github.com/xxx/yyy`
  - `https://raw.githubusercontent.com/.../file.jsonl`

数据格式可能包括：
- json, jsonl, parquet, csv, txt, markdown
- 代码文件
- 混合结构数据

**Agent必须自动识别数据结构。**

---

## 📐 输出数据规范

必须使用 **JSONL** 格式
- 每一行必须是合法 JSON 对象
- 每条数据必须包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 全局唯一ID |
| `type` | string | 数据类型 |
| `text` | string | 训练文本内容 |

**示例：**
```json
{"id":"openclaw_00000001","type":"pretrain","text":"训练文本内容"}
```

---

## 🧠 数据处理规则

### 1️⃣ 文本构造规则

Agent必须：
- 将原始数据中有语义价值的字段合并为训练文本
- 保持尽可能自然的结构（如标题+正文）
- 删除空字段 / null / 无意义字段

### 2️⃣ 特殊字符安全处理

必须保证：
- 输出 JSONL 永远可解析
- 正确处理以下字符：`[ ] { } " ' \n \t \r \`

**要求：**
- 正确转义
- 不允许产生非法JSON
- 不允许截断字符串导致结构损坏

### 3️⃣ 上下文长度控制

**最大上下文长度：4096 tokens**

规则：
- 必须使用 tokenizer 计算 token 数
- 超过 4096 token 的文本必须自动切分为多条数据
- 不允许因长度问题直接丢弃高质量文本
- 切分时应尽量保持语义完整

### 4️⃣ ID生成规则

必须生成全局唯一ID：`openclaw_{递增整数}`

要求：
- 同一次运行中不可重复
- 尽量保证可复现

### 5️⃣ type字段推断规则

Agent应根据内容自动推断类型：

| 类型 | 说明 |
|------|------|
| `pretrain` | 预训练数据 |
| `code` | 代码数据 |
| `math` | 数学数据 |
| `instruction` | 指令数据 |
| `chat` | 对话数据 |
| `webtext` | 网页文本 |
| `paper` | 论文数据 |

如果无法判断，默认使用 `pretrain`

### 6️⃣ 数据分片规则（Sharding）

必须按 shard 保存：
- 每个 JSONL 文件最大：**100000 条数据**
- 命名格式：`dataset_part_00000.jsonl`, `dataset_part_00001.jsonl`...

---

## 📊 数据质量处理建议（必须尽量执行）

Agent应尝试：
- [ ] 去除完全重复文本
- [ ] 删除极短文本（少于20字符）
- [ ] 删除base64 / 二进制噪声
- [ ] 删除大量HTML模板噪声
- [ ] 压缩重复空白字符
- [ ] 去除明显乱码

---

## 📂 GitHub 仓库要求

Agent必须创建并上传以下结构：

```
repo/
├── scripts/          # 数据处理脚本
├── examples/         # 示例输出
├── README.md         # 简要说明如何运行
└── task_spec.md      # 本任务文件
```

**必须上传：**
- 可运行的数据处理脚本
- 一个示例 JSONL 文件（≤100条数据）

**禁止上传：**
- 完整处理后的数据集

---

## 🚀 GitHub Release 要求

### 多数据集拆分发布规则（重要！）

如果原始数据集包含 **train / test / validation** 等明确划分的子集：

- **必须分开成独立的 Release 文件上传**
- **不要合并到一个 Release 中**

**正确做法：**
```
Release: v1.0-train     → 只包含 train 数据
Release: v1.0-test      → 只包含 test 数据  
Release: v1.0-validation → 只包含 validation 数据
```

**错误做法：**
```
Release: v1.0-dataset   → 包含所有数据（❌ 不符合要求）
```

### 发布步骤

Agent必须：
1. 识别数据集中的 train / test / validation 划分
2. 分别为每个子集创建独立的 tag：
   - `v1.0-train`
   - `v1.0-test`
   - `v1.0-validation`
3. 创建对应的 Release
4. 将对应子集的 JSONL 分片上传到各自的 Release

---

## ✅ 任务完成判定标准

仅当以下全部完成时任务才算成功：
- [ ] 数据处理完成
- [ ] 脚本已提交到GitHub
- [ ] 示例数据已提交
- [ ] GitHub Release 已创建
- [ ] 所有 shard 文件已上传

**Agent必须输出最终统计信息：**
```
原始样本数：
处理后样本数：
生成Shard数：
使用Tokenizer：
平均每条token数：
跳过样本数：
```

---

## ❗ 异常处理要求

Agent必须：
- 下载失败自动重试
- 跳过损坏样本
- 记录跳过数量
- 单条错误不得导致整体任务失败

---

## 🔮 能力允许时可增强

- [ ] Streaming处理超大数据集
- [ ] 多进程加速
- [ ] MinHash去重
- [ ] Token分布统计
- [ ] 多数据集混合采样
- [ ] 语言检测过滤

---

## 📚 参考实现

已有参考实现：
- `data_process/medical-kg-pretrain/` - 医学知识图谱数据处理
- `data_process/huatuo-encyclopedia-qa/` - 医学百科QA数据处理

---

*最后更新: 2026-03-23*

#!/usr/bin/env python3
"""
ScienceQA Dataset Processor
处理 derek-thomas/ScienceQA 数据集
转换为标准 JSONL 格式
"""

import json
import os
from datasets import load_dataset

# 配置
DATASET_NAME = "derek-thomas/ScienceQA"
OUTPUT_DIR = "./output"
EXAMPLES_DIR = "./examples"
SHARD_SIZE = 100000

def format_record(record, idx):
    """将原始记录转换为标准格式"""
    # 提取关键字段
    question = record.get('question', '')
    choices = record.get('choices', [])
    answer_idx = record.get('answer', 0)
    solution = record.get('solution', '')
    lecture = record.get('lecture', '')
    subject = record.get('subject', '')
    topic = record.get('topic', '')
    category = record.get('category', '')
    skill = record.get('skill', '')
    hint = record.get('hint', '')
    
    # 将answer索引转换为字母
    choice_labels = ['A', 'B', 'C', 'D', 'E', 'F']
    if isinstance(answer_idx, int) and 0 <= answer_idx < len(choice_labels):
        answer = choice_labels[answer_idx]
    else:
        answer = str(answer_idx)
    
    # 构建选项文本
    choices_text = ""
    if choices and isinstance(choices, list):
        choices_parts = []
        for i, choice in enumerate(choices):
            label = choice_labels[i] if i < len(choice_labels) else str(i+1)
            choices_parts.append(f"{label}. {choice}")
        choices_text = "\n".join(choices_parts)
    
    # 构建训练文本
    parts = []
    if subject:
        parts.append(f"【学科】{subject}")
    if topic:
        parts.append(f"【主题】{topic}")
    if category:
        parts.append(f"【类别】{category}")
    if skill:
        parts.append(f"【技能】{skill}")
    if lecture:
        parts.append(f"【知识点】{lecture}")
    if hint:
        parts.append(f"【提示】{hint}")
    if question:
        parts.append(f"【问题】{question}")
    if choices_text:
        parts.append(f"【选项】\n{choices_text}")
    if solution:
        parts.append(f"【解析】{solution}")
    if answer:
        parts.append(f"【答案】{answer}")
    
    text = "\n\n".join(parts)
    
    return {
        "id": f"openclaw_{idx:08d}",
        "type": "instruction",
        "text": text
    }

def process_dataset():
    """主处理函数"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(EXAMPLES_DIR, exist_ok=True)
    
    print(f"Loading dataset: {DATASET_NAME}")
    
    try:
        # 加载数据集
        dataset = load_dataset(DATASET_NAME)
        print(f"Available splits: {list(dataset.keys())}")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return
    
    stats = {
        "total_original": 0,
        "total_processed": 0,
        "skipped": 0,
        "splits": {}
    }
    
    # 处理每个split
    for split_name in dataset.keys():
        print(f"\nProcessing split: {split_name}")
        split_data = dataset[split_name]
        
        original_count = len(split_data)
        stats["total_original"] += original_count
        
        processed_records = []
        skipped = 0
        
        for idx, record in enumerate(split_data):
            try:
                formatted = format_record(record, stats["total_processed"] + len(processed_records))
                text = formatted["text"]
                
                # 跳过空文本或极短文本
                if not text or len(text.strip()) < 20:
                    skipped += 1
                    continue
                
                processed_records.append(formatted)
                
            except Exception as e:
                skipped += 1
                if idx < 5:
                    print(f"  Error processing record {idx}: {e}")
                continue
            
            if (idx + 1) % 1000 == 0:
                print(f"  Processed {idx + 1}/{original_count} records...")
        
        # 保存为shard
        shard_count = 0
        for i in range(0, len(processed_records), SHARD_SIZE):
            shard = processed_records[i:i + SHARD_SIZE]
            shard_file = os.path.join(OUTPUT_DIR, f"{split_name}_part_{shard_count:05d}.jsonl")
            with open(shard_file, 'w', encoding='utf-8') as f:
                for record in shard:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            shard_count += 1
        
        stats["splits"][split_name] = {
            "original": original_count,
            "processed": len(processed_records),
            "skipped": skipped,
            "shards": shard_count
        }
        stats["total_processed"] += len(processed_records)
        stats["skipped"] += skipped
        
        print(f"  Saved {len(processed_records)} records to {shard_count} shard(s)")
    
    # 保存示例文件（最多100条）
    examples = []
    for split_name in dataset.keys():
        split_file = os.path.join(OUTPUT_DIR, f"{split_name}_part_00000.jsonl")
        if os.path.exists(split_file):
            with open(split_file, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= 100:
                        break
                    examples.append(json.loads(line.strip()))
            break
    
    if examples:
        example_file = os.path.join(EXAMPLES_DIR, "examples.jsonl")
        with open(example_file, 'w', encoding='utf-8') as f:
            for record in examples[:100]:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"\nSaved {len(examples[:100])} examples to {example_file}")
    
    # 输出统计信息
    print("\n" + "="*60)
    print("处理完成统计")
    print("="*60)
    print(f"原始样本数: {stats['total_original']}")
    print(f"处理后样本数: {stats['total_processed']}")
    print(f"跳过样本数: {stats['skipped']}")
    print(f"生成Shard数: {sum(s['shards'] for s in stats['splits'].values())}")
    
    for split_name, split_stats in stats["splits"].items():
        print(f"\n{split_name}:")
        print(f"  原始: {split_stats['original']}")
        print(f"  处理后: {split_stats['processed']}")
        print(f"  跳过: {split_stats['skipped']}")
        print(f"  Shards: {split_stats['shards']}")
    
    # 保存统计信息
    with open("stats.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"\n统计信息已保存至 stats.json")

if __name__ == "__main__":
    process_dataset()

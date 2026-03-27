#!/usr/bin/env python3
"""
ScienceQA Dataset Processor - 修正版
处理parquet文件转换为JSONL格式
"""

import json
import os
import pyarrow.parquet as pq
import numpy as np

RAW_DIR = "./raw/data"
OUTPUT_DIR = "./output"
EXAMPLES_DIR = "./examples"
SHARD_SIZE = 100000

def convert_value(val):
    """转换numpy数组和其他类型为Python类型"""
    if isinstance(val, np.ndarray):
        return val.tolist()
    elif isinstance(val, (np.integer, np.floating)):
        return val.item()
    elif isinstance(val, np.bool_):
        return bool(val)
    elif isinstance(val, bytes):
        return val.decode('utf-8', errors='ignore')
    return val

def format_record(record, idx):
    """将原始记录转换为标准格式"""
    # 转换所有值
    record = {k: convert_value(v) for k, v in record.items()}
    
    question = record.get('question', '') or ''
    choices = record.get('choices', [])
    answer_idx = record.get('answer', 0)
    solution = record.get('solution', '') or record.get('rationale', '') or ''
    lecture = record.get('lecture', '') or ''
    subject = record.get('subject', '') or ''
    topic = record.get('topic', '') or ''
    category = record.get('category', '') or ''
    skill = record.get('skill', '') or ''
    hint = record.get('hint', '') or ''
    grade = record.get('grade', '') or ''
    
    # 将answer索引转换为字母
    choice_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    if isinstance(answer_idx, int) and 0 <= answer_idx < len(choice_labels):
        answer = choice_labels[answer_idx]
    else:
        answer = str(answer_idx)
    
    # 构建选项文本
    choices_text = ""
    if choices and isinstance(choices, (list, tuple)):
        choices_parts = []
        for i, choice in enumerate(choices):
            label = choice_labels[i] if i < len(choice_labels) else str(i+1)
            choice_text = str(choice) if choice else ""
            choices_parts.append(f"{label}. {choice_text}")
        choices_text = "\n".join(choices_parts)
    
    # 构建训练文本
    parts = []
    if subject:
        parts.append(f"【学科】{subject}")
    if topic:
        parts.append(f"【主题】{topic}")
    if category:
        parts.append(f"【类别】{category}")
    if grade:
        parts.append(f"【年级】{grade}")
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

def process_parquet(filepath, split_name, start_idx):
    """处理单个parquet文件"""
    print(f"\n处理: {filepath}")
    
    try:
        table = pq.read_table(filepath)
        df = table.to_pandas()
        
        total = len(df)
        print(f"  总记录数: {total}")
        
        processed = []
        skipped = 0
        
        for i, row in df.iterrows():
            try:
                formatted = format_record(row.to_dict(), start_idx + len(processed))
                text = formatted["text"]
                
                # 跳过空文本或极短文本
                if not text or len(text.strip()) < 20:
                    skipped += 1
                    continue
                
                processed.append(formatted)
                
            except Exception as e:
                skipped += 1
                if i < 3:
                    print(f"  错误处理记录 {i}: {e}")
                continue
            
            if (i + 1) % 5000 == 0:
                print(f"  已处理 {i + 1}/{total}...")
        
        print(f"  完成: {len(processed)} 条记录, 跳过 {skipped} 条")
        return processed, skipped, total
        
    except Exception as e:
        print(f"  错误读取文件: {e}")
        import traceback
        traceback.print_exc()
        return [], 0, 0

def save_shards(records, split_name):
    """保存记录为shards"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    shard_count = 0
    for i in range(0, len(records), SHARD_SIZE):
        shard = records[i:i + SHARD_SIZE]
        shard_file = os.path.join(OUTPUT_DIR, f"{split_name}_part_{shard_count:05d}.jsonl")
        
        with open(shard_file, 'w', encoding='utf-8') as f:
            for record in shard:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"  保存: {shard_file} ({len(shard)} 条)")
        shard_count += 1
    
    return shard_count

def main():
    """主函数"""
    print("="*60)
    print("ScienceQA 数据集处理器")
    print("="*60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(EXAMPLES_DIR, exist_ok=True)
    
    # 文件映射
    files = [
        ("train-00000-of-00001-1028f23e353fbe3e.parquet", "train"),
        ("validation-00000-of-00001-6c7328ff6c84284c.parquet", "validation"),
        ("test-00000-of-00001-f0e719df791966ff.parquet", "test"),
    ]
    
    stats = {
        "total_original": 0,
        "total_processed": 0,
        "skipped": 0,
        "splits": {}
    }
    
    all_examples = []
    current_idx = 0
    
    for filename, split_name in files:
        filepath = os.path.join(RAW_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"\n跳过 {filename}: 文件不存在")
            continue
        
        records, skipped, original = process_parquet(filepath, split_name, current_idx)
        
        if records:
            shard_count = save_shards(records, split_name)
            
            stats["splits"][split_name] = {
                "original": original,
                "processed": len(records),
                "skipped": skipped,
                "shards": shard_count
            }
            stats["total_original"] += original
            stats["total_processed"] += len(records)
            stats["skipped"] += skipped
            current_idx += len(records)
            
            # 收集示例
            if len(all_examples) < 100:
                all_examples.extend(records[:100 - len(all_examples)])
    
    # 保存示例
    if all_examples:
        example_file = os.path.join(EXAMPLES_DIR, "examples.jsonl")
        with open(example_file, 'w', encoding='utf-8') as f:
            for record in all_examples[:100]:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"\n保存 {len(all_examples[:100])} 条示例到 {example_file}")
    
    # 输出统计
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
    main()

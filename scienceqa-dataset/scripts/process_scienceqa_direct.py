#!/usr/bin/env python3
"""
ScienceQA Dataset Processor - Direct Download Version
使用直接下载parquet文件方式处理 derek-thomas/ScienceQA 数据集
转换为标准 JSONL 格式
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import pyarrow.parquet as pq

# 配置
DATASET_REPO = "derek-thomas/ScienceQA"
OUTPUT_DIR = "./output"
EXAMPLES_DIR = "./examples"
RAW_DIR = "./raw"
SHARD_SIZE = 100000

# Parquet文件URL模板
HF_BASE_URL = f"https://huggingface.co/datasets/{DATASET_REPO}/resolve/main/data"

def download_with_hf_cli():
    """使用huggingface-cli下载数据集"""
    print(f"Downloading dataset: {DATASET_REPO}")
    
    os.makedirs(RAW_DIR, exist_ok=True)
    
    # 检查huggingface-cli是否可用
    result = subprocess.run(
        ["which", "huggingface-cli"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # 使用huggingface-cli下载
        cmd = [
            "huggingface-cli", "download",
            DATASET_REPO,
            "--repo-type", "dataset",
            "--local-dir", RAW_DIR,
            "--local-dir-use-symlinks", "False"
        ]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        return True
    else:
        print("huggingface-cli not found, trying wget...")
        return download_with_wget()

def download_with_wget():
    """使用wget直接下载parquet文件"""
    os.makedirs(RAW_DIR, exist_ok=True)
    
    # 尝试下载已知的split文件
    splits = ["train", "validation", "test"]
    downloaded = []
    
    for split in splits:
        # 尝试不同的命名模式
        urls = [
            f"{HF_BASE_URL}/{split}-00000-of-00001.parquet",
            f"{HF_BASE_URL}/{split}.parquet",
            f"{HF_BASE_URL}/data-{split}.parquet",
        ]
        
        for url in urls:
            output_file = os.path.join(RAW_DIR, f"{split}.parquet")
            cmd = ["wget", "-q", "-O", output_file, url]
            print(f"Trying: {url}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                print(f"  ✓ Downloaded {split}.parquet ({os.path.getsize(output_file)} bytes)")
                downloaded.append(split)
                break
    
    return len(downloaded) > 0

def find_parquet_files():
    """查找所有parquet文件"""
    parquet_files = []
    for root, dirs, files in os.walk(RAW_DIR):
        for file in files:
            if file.endswith('.parquet'):
                filepath = os.path.join(root, file)
                # 从文件名推断split
                filename = file.lower()
                if 'train' in filename:
                    split = 'train'
                elif 'val' in filename or 'valid' in filename:
                    split = 'validation'
                elif 'test' in filename:
                    split = 'test'
                else:
                    split = 'data'
                parquet_files.append((filepath, split))
    return parquet_files

def format_record(record, idx):
    """将原始记录转换为标准格式"""
    # 提取关键字段 - 处理pandas Series/dict
    if hasattr(record, 'to_dict'):
        record = record.to_dict()
    
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
    if choices and isinstance(choices, list):
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

def process_parquet_file(filepath, split_name, start_idx):
    """处理单个parquet文件"""
    print(f"\nProcessing {filepath} as {split_name}")
    
    try:
        # 读取parquet文件
        table = pq.read_table(filepath)
        df = table.to_pandas()
        
        original_count = len(df)
        print(f"  Loaded {original_count} records")
        
        processed_records = []
        skipped = 0
        
        for idx, row in enumerate(df.itertuples(index=False)):
            try:
                formatted = format_record(row, start_idx + len(processed_records))
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
        
        return processed_records, skipped, original_count
        
    except Exception as e:
        print(f"Error reading parquet file: {e}")
        return [], 0, 0

def save_shards(records, split_name):
    """保存记录为shards"""
    shard_count = 0
    for i in range(0, len(records), SHARD_SIZE):
        shard = records[i:i + SHARD_SIZE]
        shard_file = os.path.join(OUTPUT_DIR, f"{split_name}_part_{shard_count:05d}.jsonl")
        with open(shard_file, 'w', encoding='utf-8') as f:
            for record in shard:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        shard_count += 1
        print(f"  Saved shard: {shard_file} ({len(shard)} records)")
    return shard_count

def process_dataset():
    """主处理函数"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(EXAMPLES_DIR, exist_ok=True)
    
    # 下载数据
    print("="*60)
    print("Step 1: Downloading dataset")
    print("="*60)
    
    if not download_with_hf_cli():
        print("Failed to download dataset")
        sys.exit(1)
    
    # 查找parquet文件
    print("\n" + "="*60)
    print("Step 2: Finding parquet files")
    print("="*60)
    
    parquet_files = find_parquet_files()
    if not parquet_files:
        print("No parquet files found!")
        sys.exit(1)
    
    print(f"Found {len(parquet_files)} parquet file(s):")
    for filepath, split in parquet_files:
        print(f"  - {filepath} (split: {split})")
    
    # 处理每个文件
    print("\n" + "="*60)
    print("Step 3: Processing data")
    print("="*60)
    
    stats = {
        "total_original": 0,
        "total_processed": 0,
        "skipped": 0,
        "splits": {}
    }
    
    all_examples = []
    current_idx = 0
    
    for filepath, split_name in parquet_files:
        records, skipped, original_count = process_parquet_file(filepath, split_name, current_idx)
        
        if records:
            # 保存shards
            shard_count = save_shards(records, split_name)
            
            stats["splits"][split_name] = {
                "original": original_count,
                "processed": len(records),
                "skipped": skipped,
                "shards": shard_count
            }
            stats["total_original"] += original_count
            stats["total_processed"] += len(records)
            stats["skipped"] += skipped
            current_idx += len(records)
            
            # 收集示例
            if len(all_examples) < 100:
                all_examples.extend(records[:100 - len(all_examples)])
    
    # 保存示例文件
    if all_examples:
        example_file = os.path.join(EXAMPLES_DIR, "examples.jsonl")
        with open(example_file, 'w', encoding='utf-8') as f:
            for record in all_examples[:100]:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"\nSaved {len(all_examples[:100])} examples to {example_file}")
    
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
    
    return stats

if __name__ == "__main__":
    process_dataset()

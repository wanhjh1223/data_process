#!/usr/bin/env python3
"""
CaseHOLD 数据集处理脚本 (Parquet 版本)
严格按照 data_process/TASK_SPEC.md 规范处理
"""

import os
import json
import sys
import gzip
from pathlib import Path
from typing import List, Dict, Any, Iterator
import pandas as pd

# 尝试加载 tokenizer
try:
    from transformers import AutoTokenizer
    TOKENIZER = AutoTokenizer.from_pretrained("gpt2")
    print(f"✅ 已加载 tokenizer: gpt2")
except Exception as e:
    TOKENIZER = None
    print(f"⚠️ 无法加载 tokenizer: {e}")
    print(f"   将使用字符数估算（约4字符=1token）")


MAX_TOKENS = 4096
CHARS_PER_TOKEN = 4
SHARD_SIZE = 100000


def count_tokens(text: str) -> int:
    """计算 token 数量"""
    if TOKENIZER:
        return len(TOKENIZER.encode(text, add_special_tokens=False))
    else:
        return len(text) // CHARS_PER_TOKEN


def split_text(text: str, max_tokens: int = MAX_TOKENS) -> List[str]:
    """将超长文本切分为多块"""
    tokens = count_tokens(text)
    if tokens <= max_tokens:
        return [text]
    
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = count_tokens(para)
        
        if current_tokens + para_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = para
            current_tokens = para_tokens
        else:
            current_chunk += "\n\n" + para if current_chunk else para
            current_tokens += para_tokens
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text[:max_tokens * CHARS_PER_TOKEN]]


def process_record(ex: Dict, global_id: int) -> Iterator[Dict[str, Any]]:
    """处理单条记录"""
    context = ex.get("context", "")
    endings = list(ex.get("endings", []))
    label = int(ex.get("label", 0))
    
    if not context or not endings:
        return
    
    correct_holding = endings[label] if label < len(endings) else ""
    full_text = context.replace("¡HOLDING¿", correct_holding)
    
    text_chunks = split_text(full_text, MAX_TOKENS)
    
    for chunk in text_chunks:
        if len(chunk.strip()) < 20:
            continue
            
        yield {
            "id": f"openclaw_{global_id:08d}",
            "type": "pretrain",
            "text": chunk.strip()
        }
        global_id += 1


def save_shard(data: List[Dict], output_dir: Path, shard_idx: int, split_name: str):
    """保存单个 shard 文件（gzip 压缩）"""
    filename = output_dir / f"{split_name}_part_{shard_idx:05d}.jsonl.gz"
    with gzip.open(filename, "wt", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return filename


def process_parquet(input_file: Path, split_name: str, output_dir: Path) -> Dict[str, Any]:
    """处理 parquet 文件"""
    print(f"\n{'='*60}")
    print(f"处理 {split_name} 划分")
    print(f"{'='*60}")
    
    print(f"📖 读取 {input_file}...")
    df = pd.read_parquet(input_file)
    examples = df.to_dict("records")
    print(f"✅ 读取完成: {len(examples):,} 条原始数据")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    stats = {
        "original_count": len(examples),
        "processed_count": 0,
        "shard_count": 0,
        "skipped_count": 0,
        "avg_tokens": 0
    }
    
    current_shard = []
    shard_idx = 0
    global_id = 1
    total_tokens = 0
    
    for i, ex in enumerate(examples):
        if i % 5000 == 0:
            print(f"  处理进度: {i}/{len(examples)} ({i/len(examples)*100:.1f}%)")
        
        try:
            for record in process_record(ex, global_id):
                current_shard.append(record)
                global_id += 1
                stats["processed_count"] += 1
                total_tokens += count_tokens(record["text"])
                
                if len(current_shard) >= SHARD_SIZE:
                    filename = save_shard(current_shard, output_dir, shard_idx, split_name)
                    print(f"  💾 保存: {filename.name} ({len(current_shard):,} 条)")
                    shard_idx += 1
                    stats["shard_count"] += 1
                    current_shard = []
                    
        except Exception as e:
            stats["skipped_count"] += 1
            continue
    
    if current_shard:
        filename = save_shard(current_shard, output_dir, shard_idx, split_name)
        print(f"  💾 保存: {filename.name} ({len(current_shard):,} 条)")
        stats["shard_count"] += 1
    
    if stats["processed_count"] > 0:
        stats["avg_tokens"] = total_tokens / stats["processed_count"]
    
    return stats


def save_examples(data: List[Dict], output_dir: Path, split_name: str, max_examples: int = 100):
    """保存示例文件"""
    examples = data[:max_examples]
    filename = output_dir / f"{split_name}_examples.jsonl"
    with open(filename, "w", encoding="utf-8") as f:
        for item in examples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return filename, len(examples)


def main():
    print("=" * 60)
    print("CaseHOLD 数据集处理 (TASK_SPEC 规范)")
    print("=" * 60)
    
    base_dir = Path(".")
    output_dir = base_dir / "processed"
    examples_dir = base_dir / "examples"
    
    output_dir.mkdir(exist_ok=True)
    examples_dir.mkdir(exist_ok=True)
    
    # 处理 train
    train_stats = process_parquet(base_dir / "train.parquet", "train", output_dir)
    
    # 处理 validation
    val_stats = process_parquet(base_dir / "validation.parquet", "validation", output_dir)
    
    # 生成示例文件
    print("\n📄 生成示例文件...")
    
    # 从处理后的数据中取样
    train_examples = []
    val_examples = []
    
    train_df = pd.read_parquet("train.parquet")
    for i, ex in enumerate(train_df.to_dict("records")[:150]):
        for record in process_record(ex, 1):
            train_examples.append(record)
            if len(train_examples) >= 100:
                break
        if len(train_examples) >= 100:
            break
    
    val_df = pd.read_parquet("validation.parquet")
    for i, ex in enumerate(val_df.to_dict("records")[:150]):
        for record in process_record(ex, 1):
            val_examples.append(record)
            if len(val_examples) >= 100:
                break
        if len(val_examples) >= 100:
            break
    
    train_ex_file, train_ex_count = save_examples(train_examples, examples_dir, "train")
    val_ex_file, val_ex_count = save_examples(val_examples, examples_dir, "validation")
    print(f"  ✓ {train_ex_file.name} ({train_ex_count} 条)")
    print(f"  ✓ {val_ex_file.name} ({val_ex_count} 条)")
    
    # 输出统计
    print("\n" + "=" * 60)
    print("📊 处理统计")
    print("=" * 60)
    print(f"\n【Train 划分】")
    print(f"  原始样本数: {train_stats['original_count']:,}")
    print(f"  处理后样本数: {train_stats['processed_count']:,}")
    print(f"  生成 Shard 数: {train_stats['shard_count']}")
    print(f"  跳过样本数: {train_stats['skipped_count']}")
    print(f"  平均 Token 数: {train_stats['avg_tokens']:.1f}")
    
    print(f"\n【Validation 划分】")
    print(f"  原始样本数: {val_stats['original_count']:,}")
    print(f"  处理后样本数: {val_stats['processed_count']:,}")
    print(f"  生成 Shard 数: {val_stats['shard_count']}")
    print(f"  跳过样本数: {val_stats['skipped_count']}")
    print(f"  平均 Token 数: {val_stats['avg_tokens']:.1f}")
    
    print(f"\n{'='*60}")
    print(f"✅ 处理完成！")
    print(f"输出目录: {output_dir.absolute()}")
    print(f"示例目录: {examples_dir.absolute()}")
    print(f"{'='*60}")
    
    print("\n📁 输出文件:")
    for f in sorted(output_dir.glob("*.gz")):
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"   {f.name:<40} {size_mb:>8.2f} MB")
    
    # 保存统计到文件
    with open(base_dir / "stats.json", "w") as f:
        json.dump({
            "train": train_stats,
            "validation": val_stats,
            "tokenizer": "gpt2" if TOKENIZER else "chars_per_token_4"
        }, f, indent=2)
    
    return train_stats, val_stats


if __name__ == "__main__":
    main()

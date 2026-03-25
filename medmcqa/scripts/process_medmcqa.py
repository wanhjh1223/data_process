#!/usr/bin/env python3
"""
MedMCQA 数据集处理脚本 - 指令微调格式
来源: https://huggingface.co/datasets/openlifescienceai/medmcqa

格式示例:
{
  "id": "openclaw_00000001",
  "type": "instruction",
  "text": "There is a single choice question about medical. Answer the question by replying A, B, C or D.\nQuestion: xxx\n\nOption A: xxx\nOption B: xxx\nOption C: xxx\nOption D: xxx\nAnswer: \nC\n\nExplanation: xxx"
}
"""

import json
import gzip
import os
from pathlib import Path
import pandas as pd

# 配置
SHARD_SIZE = 100000

# 本地缓存路径
CACHE_DIR = Path.home() / ".cache/huggingface/hub/datasets--openlifescienceai--medmcqa/snapshots/91c6572c454088bf71b679ad90aa8dffcd0d5868/data"


def format_record(ex, global_id):
    """将单条记录格式化为指令微调格式（仅处理 single choice）"""
    question = str(ex.get("question", "")).strip()
    
    # 仅处理 single choice 类型
    instruction_prefix = "There is a single choice question about medical. Answer the question by replying A, B, C or D."
    
    # 获取选项
    opa = str(ex.get("opa", "")).strip()
    opb = str(ex.get("opb", "")).strip()
    opc = str(ex.get("opc", "")).strip()
    opd = str(ex.get("opd", "")).strip()
    
    # 获取正确答案
    cop = ex.get("cop", -1)  # correct option index (0=A, 1=B, 2=C, 3=D)
    answer_map = {0: "A", 1: "B", 2: "C", 3: "D"}
    answer = answer_map.get(cop, "")
    
    # 获取解释（exp 字段可能为空）
    explanation = str(ex.get("exp", "")).strip()
    
    # 构造文本
    text_parts = [instruction_prefix]
    text_parts.append(f"Question: {question}")
    text_parts.append("")  # 空行
    
    # 添加选项 - 格式: Option A: xxx
    if opa:
        text_parts.append(f"Option A: {opa}")
    if opb:
        text_parts.append(f"Option B: {opb}")
    if opc:
        text_parts.append(f"Option C: {opc}")
    if opd:
        text_parts.append(f"Option D: {opd}")
    
    # 添加答案（单独一行）
    if answer:
        text_parts.append(f"Answer: ")
        text_parts.append(answer)
    
    # 添加解释（如果有）
    if explanation:
        text_parts.append("")
        text_parts.append(f"Explanation: {explanation}")
    
    full_text = "\n".join(text_parts)
    
    return {
        "id": f"openclaw_{global_id:08d}",
        "type": "instruction",
        "text": full_text
    }


def process_split(split_name, parquet_path, output_dir, start_id=1):
    """处理单个 split"""
    print(f"\n{'='*50}")
    print(f"处理 {split_name} 数据集...")
    print(f"来源: {parquet_path}")
    print('='*50)
    
    # 流式读取 parquet
    print(f"  📖 读取 parquet 文件...")
    df = pd.read_parquet(parquet_path)
    total_raw = len(df)
    
    # 过滤掉 multi 类型样本（数据存在不一致性）
    print(f"  🔄 过滤 multi choice 样本...")
    df = df[df['choice_type'] == 'single']
    total = len(df)
    filtered = total_raw - total
    print(f"  ✅ 共 {total:,} 条 (过滤掉 {filtered:,} 条 multi 类型)")
    
    # 处理数据
    current_shard = []
    shard_idx = 0
    global_id = start_id
    processed_count = 0
    skipped_count = 0
    
    for idx in range(total):
        if idx % 10000 == 0 and idx > 0:
            print(f"  处理进度: {idx:,} / {total:,} ({idx/total*100:.1f}%)")
        
        try:
            ex = df.iloc[idx]
            record = format_record(ex, global_id)
            
            # 检查文本质量
            if len(record["text"]) < 50:
                skipped_count += 1
                continue
            
            current_shard.append(record)
            global_id += 1
            processed_count += 1
            
            # 达到 shard 大小，保存文件
            if len(current_shard) >= SHARD_SIZE:
                filename = output_dir / f"medmcqa_{split_name}_part_{shard_idx:05d}.jsonl.gz"
                with gzip.open(filename, "wt", encoding="utf-8") as f:
                    for item in current_shard:
                        f.write(json.dumps(item, ensure_ascii=False) + "\n")
                print(f"  💾 保存: {filename.name} ({len(current_shard):,} 条)")
                shard_idx += 1
                current_shard = []
                
        except Exception as e:
            skipped_count += 1
            continue
    
    # 保存最后一个 shard
    if current_shard:
        filename = output_dir / f"medmcqa_{split_name}_part_{shard_idx:05d}.jsonl.gz"
        with gzip.open(filename, "wt", encoding="utf-8") as f:
            for item in current_shard:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"  💾 保存: {filename.name} ({len(current_shard):,} 条)")
        shard_idx += 1
    
    print(f"  ✓ {split_name} 完成: {processed_count:,} / {total:,} 条")
    
    return {
        "processed": processed_count,
        "shards": shard_idx,
        "skipped": skipped_count,
        "total": total,
        "next_id": global_id
    }


def main():
    print("=" * 60)
    print("MedMCQA 数据集处理 - 指令微调格式")
    print("=" * 60)
    
    base_dir = Path(".")
    output_dir = base_dir / "processed"
    examples_dir = base_dir / "examples"
    
    output_dir.mkdir(exist_ok=True)
    examples_dir.mkdir(exist_ok=True)
    
    # 清空旧的 processed 目录
    print("\n🗑️  清理旧的处理文件...")
    for f in output_dir.glob("*.jsonl.gz"):
        f.unlink()
        print(f"   删除: {f.name}")
    
    # 检查缓存文件
    print("\n📂 检查本地缓存...")
    splits = {
        "train": CACHE_DIR / "train-00000-of-00001.parquet",
        "validation": CACHE_DIR / "validation-00000-of-00001.parquet",
        "test": CACHE_DIR / "test-00000-of-00001.parquet"
    }
    
    for split_name, path in splits.items():
        if path.exists():
            print(f"   ✅ {split_name}: {path.name}")
        else:
            print(f"   ❌ {split_name}: 未找到")
    
    # 处理各个 split
    all_stats = {}
    current_id = 1
    
    for split_name, parquet_path in splits.items():
        if not parquet_path.exists():
            print(f"\n⚠️  跳过 {split_name} (文件不存在)")
            continue
        
        stats = process_split(split_name, parquet_path, output_dir, current_id)
        all_stats[split_name] = stats
        current_id = stats["next_id"]
    
    # 生成示例文件（从 train 取前100条 single choice）
    print("\n📄 生成示例文件...")
    examples = []
    try:
        train_path = splits["train"]
        if train_path.exists():
            df = pd.read_parquet(train_path)
            # 过滤 single choice
            df = df[df['choice_type'] == 'single']
            for i in range(min(100, len(df))):
                record = format_record(df.iloc[i], i + 1)
                if len(record["text"]) >= 50:
                    examples.append(record)
    except Exception as e:
        print(f"  ⚠️ 生成示例失败: {e}")
    
    with open(examples_dir / "examples.jsonl", "w", encoding="utf-8") as f:
        for item in examples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"  ✓ examples.jsonl ({len(examples)} 条)")
    
    # 输出统计
    print("\n" + "=" * 60)
    print("📊 处理统计")
    print("=" * 60)
    total_processed = 0
    for split, stats in all_stats.items():
        print(f"{split}:")
        print(f"  原始数据: {stats['total']:,} 条")
        print(f"  处理后: {stats['processed']:,} 条")
        print(f"  Shards: {stats['shards']}")
        print(f"  跳过: {stats['skipped']}")
        total_processed += stats['processed']
    
    print(f"\n总计处理: {total_processed:,} 条")
    
    print("\n📁 输出文件:")
    for f in sorted(output_dir.glob("*.gz")):
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"   {f.name:<50} {size_mb:>6.2f} MB")
    
    # 保存统计
    with open(base_dir / "stats.json", "w") as f:
        json.dump({
            "dataset": "openlifescienceai/medmcqa",
            "format": "instruction",
            "splits": {k: {kk: vv for kk, vv in v.items() if kk != 'next_id'} for k, v in all_stats.items()},
            "total_processed": total_processed
        }, f, indent=2)
    
    print(f"\n✅ 完成！")


if __name__ == "__main__":
    main()

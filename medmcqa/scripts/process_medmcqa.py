#!/usr/bin/env python3
"""
MedMCQA 数据集处理脚本
来源: https://huggingface.co/datasets/openlifescienceai/medmcqa
"""

import json
import gzip
from pathlib import Path
from datasets import load_dataset

# 配置
SHARD_SIZE = 100000

def main():
    print("=" * 60)
    print("MedMCQA 数据集处理")
    print("=" * 60)
    
    base_dir = Path(".")
    output_dir = base_dir / "processed"
    examples_dir = base_dir / "examples"
    
    output_dir.mkdir(exist_ok=True)
    examples_dir.mkdir(exist_ok=True)
    
    # 加载数据集
    print("\n📥 加载 MedMCQA 数据集...")
    print("   Dataset: openlifescienceai/medmcqa")
    
    splits_to_process = ["train", "validation", "test"]
    all_stats = {}
    
    for split_name in splits_to_process:
        print(f"\n{'='*50}")
        print(f"处理 {split_name} 数据集...")
        print('='*50)
        
        try:
            dataset = load_dataset("openlifescienceai/medmcqa", split=split_name, streaming=True)
        except Exception as e:
            print(f"  ⚠️ {split_name} 加载失败: {e}")
            continue
        
        # 处理数据
        current_shard = []
        shard_idx = 0
        global_id = 1
        processed_count = 0
        skipped_count = 0
        
        for i, ex in enumerate(dataset):
            if i % 10000 == 0 and i > 0:
                print(f"  处理进度: {i:,} 条 (已处理: {processed_count:,})")
            
            try:
                # 构造训练文本
                question = ex.get("question", "")
                options = {
                    "A": ex.get("opa", ""),
                    "B": ex.get("opb", ""),
                    "C": ex.get("opc", ""),
                    "D": ex.get("opd", "")
                }
                answer_idx = ex.get("cop", -1)  # correct option
                answer = ex.get("answer", "")
                explanation = ex.get("exp", "")
                
                if not question:
                    skipped_count += 1
                    continue
                
                text_parts = [f"Question: {question}"]
                
                # 添加选项
                for opt, val in options.items():
                    if val:
                        text_parts.append(f"Option {opt}: {val}")
                
                # 添加答案
                if answer:
                    text_parts.append(f"Answer: {answer}")
                elif answer_idx >= 0:
                    answer_map = ["A", "B", "C", "D"]
                    if answer_idx < len(answer_map):
                        text_parts.append(f"Answer: {answer_map[answer_idx]}")
                
                # 添加解释
                if explanation:
                    text_parts.append(f"Explanation: {explanation}")
                
                full_text = "\n\n".join(text_parts)
                
                if len(full_text.strip()) < 50:
                    skipped_count += 1
                    continue
                
                record = {
                    "id": f"openclaw_{global_id:08d}",
                    "type": "instruction",
                    "text": full_text.strip()
                }
                
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
        
        all_stats[split_name] = {
            "processed": processed_count,
            "shards": shard_idx,
            "skipped": skipped_count
        }
        
        print(f"  ✓ {split_name} 完成: {processed_count:,} 条")
    
    # 保存示例（取 train 的前100条）
    print("\n📄 生成示例文件...")
    examples = []
    try:
        dataset = load_dataset("openlifescienceai/medmcqa", split="train", streaming=True)
        for i, ex in enumerate(dataset):
            if i >= 100:
                break
            question = ex.get("question", "")
            options = {
                "A": ex.get("opa", ""),
                "B": ex.get("opb", ""),
                "C": ex.get("opc", ""),
                "D": ex.get("opd", "")
            }
            answer = ex.get("answer", "")
            explanation = ex.get("exp", "")
            
            text_parts = [f"Question: {question}"]
            for opt, val in options.items():
                if val:
                    text_parts.append(f"Option {opt}: {val}")
            if answer:
                text_parts.append(f"Answer: {answer}")
            if explanation:
                text_parts.append(f"Explanation: {explanation}")
            
            examples.append({
                "id": f"openclaw_{i+1:08d}",
                "type": "instruction",
                "text": "\n\n".join(text_parts).strip()
            })
    except:
        pass
    
    with open(examples_dir / "examples.jsonl", "w", encoding="utf-8") as f:
        for item in examples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"  ✓ examples.jsonl ({len(examples)} 条)")
    
    # 输出统计
    print("\n" + "=" * 60)
    print("📊 处理统计")
    print("=" * 60)
    for split, stats in all_stats.items():
        print(f"{split}:")
        print(f"  处理后: {stats['processed']:,} 条")
        print(f"  Shards: {stats['shards']}")
        print(f"  跳过: {stats['skipped']}")
    
    print("\n📁 输出文件:")
    for f in sorted(output_dir.glob("*.gz")):
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"   {f.name:<50} {size_mb:>6.2f} MB")
    
    # 保存统计
    with open(base_dir / "stats.json", "w") as f:
        json.dump({
            "dataset": "openlifescienceai/medmcqa",
            "splits": all_stats
        }, f, indent=2)
    
    print(f"\n✅ 完成！")


if __name__ == "__main__":
    main()

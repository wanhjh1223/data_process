#!/usr/bin/env python3
"""
PHYSICS 数据集处理脚本 (修正版)
来源: https://huggingface.co/datasets/desimfj/PHYSICS
"""

import json
import gzip
from pathlib import Path
from datasets import load_dataset

SHARD_SIZE = 100000

def main():
    print("=" * 60)
    print("PHYSICS 数据集处理")
    print("=" * 60)
    
    base_dir = Path(".")
    output_dir = base_dir / "processed"
    examples_dir = base_dir / "examples"
    
    output_dir.mkdir(exist_ok=True)
    examples_dir.mkdir(exist_ok=True)
    
    print("\n📥 加载 PHYSICS 数据集...")
    print("   Dataset: desimfj/PHYSICS")
    
    try:
        dataset = load_dataset("desimfj/PHYSICS", split="test", streaming=True)
        print("   ✓ test 分割加载成功")
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")
        return
    
    print("\n处理 test...")
    
    current_shard = []
    shard_idx = 0
    global_id = 1
    processed_count = 0
    
    for i, ex in enumerate(dataset):
        if i % 1000 == 0 and i > 0:
            print(f"  进度: {i:,} (已处理: {processed_count:,})")
        
        try:
            question = ex.get("question", "")
            solution = ex.get("solution", "")
            answer = ex.get("answer", [])
            
            if not question:
                continue
            
            text_parts = [f"Question: {question}"]
            
            if solution:
                text_parts.append(f"Solution: {solution}")
            
            if answer:
                # answer 是列表的列表，需要展平
                answer_texts = []
                for ans_list in answer:
                    if isinstance(ans_list, list):
                        answer_texts.extend(ans_list)
                    else:
                        answer_texts.append(str(ans_list))
                if answer_texts:
                    text_parts.append(f"Answer: {', '.join(answer_texts)}")
            
            full_text = "\n\n".join(text_parts)
            if len(full_text.strip()) < 50:
                continue
            
            current_shard.append({
                "id": f"openclaw_{global_id:08d}",
                "type": "instruction",
                "text": full_text.strip()
            })
            global_id += 1
            processed_count += 1
            
            if len(current_shard) >= SHARD_SIZE:
                filename = output_dir / f"physics_test_part_{shard_idx:05d}.jsonl.gz"
                with gzip.open(filename, "wt", encoding="utf-8") as f:
                    for item in current_shard:
                        f.write(json.dumps(item, ensure_ascii=False) + "\n")
                print(f"  💾 {filename.name} ({len(current_shard):,})")
                shard_idx += 1
                current_shard = []
                
        except Exception as e:
            continue
    
    if current_shard:
        filename = output_dir / f"physics_test_part_{shard_idx:05d}.jsonl.gz"
        with gzip.open(filename, "wt", encoding="utf-8") as f:
            for item in current_shard:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"  💾 {filename.name} ({len(current_shard):,})")
        shard_idx += 1
    
    print(f"  ✓ test: {processed_count:,} 条")
    
    # 示例
    print("\n📄 生成示例...")
    examples = current_shard[:100] if len(current_shard) >= 100 else current_shard
    with open(examples_dir / "examples.jsonl", "w") as f:
        for item in examples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"  ✓ examples.jsonl ({len(examples)})")
    
    # 统计
    print("\n" + "=" * 60)
    print("📊 统计")
    print("=" * 60)
    print(f"test: {processed_count:,} 条, {shard_idx} shards")
    
    with open(base_dir / "stats.json", "w") as f:
        json.dump({"dataset": "desimfj/PHYSICS", "test": {"processed": processed_count, "shards": shard_idx}}, f, indent=2)
    
    print("\n✅ 完成！")

if __name__ == "__main__":
    main()

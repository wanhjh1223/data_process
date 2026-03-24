#!/usr/bin/env python3
"""
MedQA 数据集处理脚本
处理解压后的 data_clean 目录
"""

import json
import gzip
from pathlib import Path

SHARD_SIZE = 100000

def process_jsonl_file(filepath):
    """处理单个 JSONL 文件"""
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except:
                    pass
    return records

def main():
    print("=" * 60)
    print("MedQA 数据集处理")
    print("=" * 60)
    
    base_dir = Path(".")
    output_dir = base_dir / "processed"
    examples_dir = base_dir / "examples"
    data_dir = base_dir / "data_clean" / "questions"
    
    output_dir.mkdir(exist_ok=True)
    examples_dir.mkdir(exist_ok=True)
    
    # 处理各个地区的数据
    regions = ["US", "Mainland", "Taiwan"]
    all_data = {"train": [], "test": [], "dev": []}
    
    for region in regions:
        region_dir = data_dir / region
        if not region_dir.exists():
            continue
        
        print(f"\n处理 {region} 数据...")
        
        for split in ["train", "test", "dev"]:
            # 查找 JSONL 文件
            jsonl_files = list(region_dir.glob(f"{split}.jsonl"))
            if not jsonl_files:
                # 尝试其他路径
                jsonl_files = list((region_dir / "4_options").glob(f"{split}.jsonl"))
            
            for filepath in jsonl_files:
                records = process_jsonl_file(filepath)
                print(f"  {filepath.name}: {len(records)} 条")
                all_data[split].extend(records)
    
    # 处理并保存
    print("\n" + "=" * 60)
    print("处理并保存数据...")
    print("=" * 60)
    
    split_names = {"train": "train", "dev": "validation", "test": "test"}
    all_stats = {}
    
    for split, records in all_data.items():
        if not records:
            continue
        
        output_split = split_names[split]
        print(f"\n处理 {output_split}: {len(records)} 条原始数据")
        
        current_shard = []
        shard_idx = 0
        global_id = 1
        processed_count = 0
        
        for i, ex in enumerate(records):
            if i % 5000 == 0 and i > 0:
                print(f"  进度: {i:,} / {len(records):,}")
            
            try:
                question = ex.get("question", "")
                options = ex.get("options", []) or []
                answer = ex.get("answer", "") or ex.get("answer_idx", "")
                
                if not question:
                    continue
                
                text_parts = [f"Question: {question}"]
                
                if options and isinstance(options, list):
                    for idx, opt in enumerate(options):
                        if opt:
                            text_parts.append(f"Option {chr(65+idx)}: {opt}")
                
                if answer:
                    text_parts.append(f"Answer: {answer}")
                
                full_text = "\n\n".join(text_parts)
                if len(full_text.strip()) < 30:
                    continue
                
                current_shard.append({
                    "id": f"openclaw_{global_id:08d}",
                    "type": "instruction",
                    "text": full_text.strip()
                })
                global_id += 1
                processed_count += 1
                
                if len(current_shard) >= SHARD_SIZE:
                    filename = output_dir / f"medqa_{output_split}_part_{shard_idx:05d}.jsonl.gz"
                    with gzip.open(filename, "wt", encoding="utf-8") as f:
                        for item in current_shard:
                            f.write(json.dumps(item, ensure_ascii=False) + "\n")
                    print(f"  💾 {filename.name} ({len(current_shard):,})")
                    shard_idx += 1
                    current_shard = []
                    
            except Exception as e:
                continue
        
        if current_shard:
            filename = output_dir / f"medqa_{output_split}_part_{shard_idx:05d}.jsonl.gz"
            with gzip.open(filename, "wt", encoding="utf-8") as f:
                for item in current_shard:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            print(f"  💾 {filename.name} ({len(current_shard):,})")
            shard_idx += 1
        
        all_stats[output_split] = {"processed": processed_count, "shards": shard_idx}
        print(f"  ✓ {output_split}: {processed_count:,} 条")
    
    # 示例
    print("\n📄 生成示例...")
    examples = []
    if all_stats.get("train", {}).get("processed", 0) > 0:
        files = list(output_dir.glob("medqa_train_*.gz"))
        if files:
            with gzip.open(files[0], "rt") as f:
                for i, line in enumerate(f):
                    if i >= 100:
                        break
                    examples.append(json.loads(line))
    
    with open(examples_dir / "examples.jsonl", "w") as f:
        for item in examples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"  ✓ examples.jsonl ({len(examples)})")
    
    # 统计
    print("\n" + "=" * 60)
    print("📊 统计")
    print("=" * 60)
    total = 0
    for split, stats in all_stats.items():
        print(f"{split}: {stats['processed']:,} 条, {stats['shards']} shards")
        total += stats['processed']
    print(f"总计: {total:,} 条")
    
    with open(base_dir / "stats.json", "w") as f:
        json.dump({"dataset": "bigbio/med_qa", "splits": all_stats, "total": total}, f, indent=2)
    
    print("\n✅ 完成！")

if __name__ == "__main__":
    main()

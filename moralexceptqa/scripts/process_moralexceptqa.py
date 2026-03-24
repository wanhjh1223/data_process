#!/usr/bin/env python3
"""
MoralExceptQA 数据集处理脚本
来源: https://huggingface.co/datasets/feradauto/MoralExceptQA
"""

import json
import gzip
from pathlib import Path
import requests

# 配置
SHARD_SIZE = 100000
DATASET_URL = "https://hf-mirror.com/datasets/feradauto/MoralExceptQA/resolve/main/data/complete_file.json"

def download_and_process():
    print("=" * 60)
    print("MoralExceptQA 数据集处理")
    print("=" * 60)
    
    base_dir = Path(".")
    output_dir = base_dir / "processed"
    examples_dir = base_dir / "examples"
    
    output_dir.mkdir(exist_ok=True)
    examples_dir.mkdir(exist_ok=True)
    
    # 下载数据
    print(f"\n📥 下载数据...")
    print(f"   URL: {DATASET_URL}")
    
    response = requests.get(DATASET_URL, timeout=60)
    response.raise_for_status()
    
    # JSON Lines 格式，逐行解析
    data = []
    for line in response.text.strip().split('\n'):
        if line:
            data.append(json.loads(line))
    
    print(f"✅ 下载完成: {len(data)} 条")
    
    # 处理数据
    print("\n🔄 处理数据...")
    
    records = []
    for i, ex in enumerate(data):
        if i % 1000 == 0 and i > 0:
            print(f"  处理进度: {i}/{len(data)}")
        
        try:
            # 构造训练文本
            text_parts = []
            
            # 添加场景描述
            if "scenario" in ex:
                text_parts.append(f"Scenario: {ex['scenario']}")
            
            # 添加问题
            if "question" in ex:
                text_parts.append(f"Question: {ex['question']}")
            
            # 添加选项
            if "choices" in ex and isinstance(ex["choices"], list):
                for idx, choice in enumerate(ex["choices"]):
                    text_parts.append(f"Option {chr(65+idx)}: {choice}")
            
            # 添加答案
            if "answer" in ex:
                text_parts.append(f"Answer: {ex['answer']}")
            
            if not text_parts:
                continue
            
            full_text = "\n\n".join(text_parts)
            
            # 过滤太短的内容
            if len(full_text.strip()) < 50:
                continue
            
            records.append({
                "id": f"openclaw_{i+1:08d}",
                "type": "instruction",
                "text": full_text.strip()
            })
            
        except Exception as e:
            continue
    
    print(f"✅ 处理完成: {len(records)} 条")
    
    # 保存数据
    print("\n💾 保存数据...")
    
    shard_idx = 0
    while records:
        shard_data = records[:SHARD_SIZE]
        records = records[SHARD_SIZE:]
        
        filename = output_dir / f"moralexceptqa_part_{shard_idx:05d}.jsonl.gz"
        with gzip.open(filename, "wt", encoding="utf-8") as f:
            for item in shard_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"  💾 保存: {filename.name} ({len(shard_data)} 条)")
        shard_idx += 1
    
    # 保存示例
    print("\n📄 生成示例文件...")
    all_records = []
    for f in sorted(output_dir.glob("*.gz")):
        with gzip.open(f, "rt", encoding="utf-8") as fp:
            for line in fp:
                all_records.append(json.loads(line))
                if len(all_records) >= 100:
                    break
        if len(all_records) >= 100:
            break
    
    examples = all_records[:100]
    with open(examples_dir / "examples.jsonl", "w", encoding="utf-8") as f:
        for item in examples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    print(f"  ✓ examples.jsonl ({len(examples)} 条)")
    
    # 输出统计
    print("\n" + "=" * 60)
    print("📊 处理统计")
    print("=" * 60)
    print(f"原始样本数: {len(data)}")
    print(f"处理后样本数: {len(all_records)}")
    print(f"生成 Shard 数: {shard_idx}")
    
    print("\n📁 输出文件:")
    for f in sorted(output_dir.glob("*.gz")):
        size_kb = f.stat().st_size / 1024
        print(f"   {f.name:<40} {size_kb:>8.1f} KB")
    
    # 保存统计
    with open(base_dir / "stats.json", "w") as f:
        json.dump({
            "dataset": "feradauto/MoralExceptQA",
            "original_count": len(data),
            "processed_count": len(all_records),
            "shards": shard_idx
        }, f, indent=2)
    
    print(f"\n✅ 完成！")


if __name__ == "__main__":
    download_and_process()

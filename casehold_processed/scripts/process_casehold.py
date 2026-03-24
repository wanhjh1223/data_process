#!/usr/bin/env python3
"""
CaseHOLD 数据集处理脚本
下载并转换为预训练格式

用法:
    python process_casehold.py
"""

import os
import json
import sys
from pathlib import Path
from datasets import load_dataset


def format_triplet(ex):
    """三联体格式"""
    endings = list(ex["endings"]) if hasattr(ex["endings"], "__iter__") else ex["endings"]
    label = int(ex["label"])
    return {
        "case_citation": ex["context"].replace("¡HOLDING¿", "").strip(),
        "holding": endings[label],
        "explanation": f"根据案例引用，法院裁决要点为：{endings[label]}",
        "legal_principle": "法律原则待提取",
        "distractors": [e for i, e in enumerate(endings) if i != label],
        "full_text": ex["context"].replace("¡HOLDING¿", endings[label])
    }


def format_instruction(ex):
    """指令微调格式"""
    endings = list(ex["endings"]) if hasattr(ex["endings"], "__iter__") else ex["endings"]
    label = int(ex["label"])
    context = ex["context"].replace("¡HOLDING¿", "[HOLDING]")
    choices_text = "\n".join([f"{chr(65+i)}. {e}" for i, e in enumerate(endings)])
    answer = f"{chr(65+label)}. {endings[label]}"
    
    return {
        "instruction": "根据以下法院判决引用，确定正确的法律裁决要点：",
        "input": f"{context}\n\n选项：\n{choices_text}",
        "output": f"正确答案是：{answer}",
        "label": label,
        "choices": endings
    }


def format_contrastive(ex):
    """对比学习格式"""
    endings = list(ex["endings"]) if hasattr(ex["endings"], "__iter__") else ex["endings"]
    label = int(ex["label"])
    return {
        "anchor": ex["context"].replace("¡HOLDING¿", "").strip(),
        "positive": endings[label],
        "hard_negatives": [e for i, e in enumerate(endings) if i != label],
        "full_context": ex["context"].replace("¡HOLDING¿", endings[label])
    }


def save_jsonl(data, filepath):
    """保存为 JSONL 格式"""
    with open(filepath, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"  ✓ 已保存: {filepath} ({len(data):,} 条)")


def process_split(dataset, split_name, output_dir):
    """处理单个数据划分"""
    print(f"\n📊 处理 {split_name} 划分 ({len(dataset):,} 条)...")
    examples = list(dataset)
    
    # 三联体格式
    print(f"  🔄 生成三联体格式...")
    triplet_data = [format_triplet(ex) for ex in examples]
    save_jsonl(triplet_data, output_dir / f"{split_name}_triplet.jsonl")
    
    # 指令格式
    print(f"  🔄 生成指令格式...")
    instruction_data = [format_instruction(ex) for ex in examples]
    save_jsonl(instruction_data, output_dir / f"{split_name}_instruction.jsonl")
    
    # 对比学习格式
    print(f"  🔄 生成对比学习格式...")
    contrastive_data = [format_contrastive(ex) for ex in examples]
    save_jsonl(contrastive_data, output_dir / f"{split_name}_contrastive.jsonl")
    
    return len(examples)


def main():
    output_dir = Path(".")
    
    print("=" * 60)
    print("CaseHOLD 数据集处理")
    print("=" * 60)
    
    print("\n📥 正在下载 CaseHOLD 数据集...")
    print("   数据源: lex_glue / case_hold")
    
    try:
        dataset = load_dataset("lex_glue", "case_hold")
        print(f"\n✅ 数据集加载成功!")
        print(f"   训练集: {len(dataset['train']):,} 条")
        print(f"   验证集: {len(dataset['validation']):,} 条")
    except Exception as e:
        print(f"\n❌ 数据加载失败: {e}")
        print("   尝试使用镜像源...")
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        dataset = load_dataset("lex_glue", "case_hold")
        print(f"\n✅ 使用镜像源加载成功!")
    
    total_processed = 0
    
    # 处理训练集
    total_processed += process_split(dataset["train"], "train", output_dir)
    
    # 处理验证集
    total_processed += process_split(dataset["validation"], "validation", output_dir)
    
    print("\n" + "=" * 60)
    print(f"✅ 处理完成! 总计处理: {total_processed:,} 条")
    print("=" * 60)
    
    # 列出输出文件
    print("\n📁 输出文件:")
    for f in sorted(output_dir.glob("*.jsonl")):
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"   {f.name:<40} {size_mb:>8.2f} MB")


if __name__ == "__main__":
    main()

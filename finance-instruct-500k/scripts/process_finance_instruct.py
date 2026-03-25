#!/usr/bin/env python3
"""
Finance-Instruct-500k 数据集处理脚本
来源: ModelScope Data-by-IngeniusAI/Finance-Instruct-500k
格式: user_input + reasoning_content + answer_r1
"""

import json
import gzip
from pathlib import Path

# 配置
SHARD_SIZE = 100000
DATA_FILES = [
    "modelscope_data/Data-by-IngeniusAI/Finance_R1-Distill_data_0.jsonl",
    "modelscope_data/Data-by-IngeniusAI/Finance_R1-Distill_data_1.jsonl",
    "modelscope_data/Data-by-IngeniusAI/Finance_R1-Distill_data_2.jsonl"
]


def format_record(ex, global_id):
    """将单条记录格式化为指令微调格式"""
    user_input = ex.get("user_input", "").strip()
    reasoning = ex.get("reasoning_content", "").strip()
    answer = ex.get("answer_r1", "").strip()
    
    if not user_input or not answer:
        return None
    
    # 构造训练文本
    text_parts = [f"Instruction: {user_input}"]
    
    # 如果有推理过程，也包含进去
    if reasoning:
        text_parts.append(f"Reasoning: {reasoning}")
    
    text_parts.append(f"Output: {answer}")
    
    full_text = "\n\n".join(text_parts)
    
    # 过滤太短的内容
    if len(full_text.strip()) < 100:
        return None
    
    return {
        "id": f"openclaw_{global_id:08d}",
        "type": "instruction",
        "text": full_text.strip()
    }


def main():
    print("=" * 60)
    print("Finance-Instruct-500k 数据集处理")
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
    
    # 处理数据
    print("\n🔄 处理数据...")
    
    current_shard = []
    shard_idx = 0
    global_id = 1
    processed_count = 0
    skipped_count = 0
    
    for data_file in DATA_FILES:
        file_path = base_dir / data_file
        if not file_path.exists():
            print(f"   ⚠️ 文件不存在: {data_file}")
            continue
        
        print(f"   📖 读取: {data_file}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    ex = json.loads(line.strip())
                    record = format_record(ex, global_id)
                    
                    if record is None:
                        skipped_count += 1
                        continue
                    
                    current_shard.append(record)
                    global_id += 1
                    processed_count += 1
                    
                    # 达到 shard 大小，保存文件
                    if len(current_shard) >= SHARD_SIZE:
                        filename = output_dir / f"finance_instruct_part_{shard_idx:05d}.jsonl.gz"
                        with gzip.open(filename, "wt", encoding="utf-8") as f_out:
                            for item in current_shard:
                                f_out.write(json.dumps(item, ensure_ascii=False) + "\n")
                        print(f"  💾 保存: {filename.name} ({len(current_shard):,} 条)")
                        shard_idx += 1
                        current_shard = []
                        
                except Exception as e:
                    skipped_count += 1
                    continue
    
    # 保存最后一个 shard
    if current_shard:
        filename = output_dir / f"finance_instruct_part_{shard_idx:05d}.jsonl.gz"
        with gzip.open(filename, "wt", encoding="utf-8") as f:
            for item in current_shard:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"  💾 保存: {filename.name} ({len(current_shard):,} 条)")
        shard_idx += 1
    
    # 保存示例（取前100条）
    print("\n📄 生成示例文件...")
    examples = current_shard[:100] if len(current_shard) >= 100 else current_shard
    
    # 如果 current_shard 不足100条，从已保存的文件中读取
    if len(examples) < 100:
        saved_files = sorted(output_dir.glob("*.jsonl.gz"))
        if saved_files:
            with gzip.open(saved_files[0], "rt", encoding="utf-8") as f:
                for line in f:
                    if len(examples) >= 100:
                        break
                    examples.append(json.loads(line))
    
    with open(examples_dir / "examples.jsonl", "w", encoding="utf-8") as f:
        for item in examples[:100]:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"  ✓ examples.jsonl ({len(examples[:100])} 条)")
    
    # 输出统计
    print("\n" + "=" * 60)
    print("📊 处理统计")
    print("=" * 60)
    print(f"处理后样本数: {processed_count:,}")
    print(f"生成 Shard 数: {shard_idx}")
    print(f"跳过样本数: {skipped_count}")
    
    print("\n📁 输出文件:")
    for f in sorted(output_dir.glob("*.gz")):
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"   {f.name:<40} {size_mb:>8.2f} MB")
    
    # 保存统计
    with open(base_dir / "stats.json", "w") as f:
        json.dump({
            "dataset": "Josephgflowers/Finance-Instruct-500k",
            "source": "modelscope:Data-by-IngeniusAI/Finance-Instruct-500k",
            "processed_count": processed_count,
            "shards": shard_idx,
            "skipped": skipped_count
        }, f, indent=2)
    
    print(f"\n✅ 完成！")


if __name__ == "__main__":
    main()

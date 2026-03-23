#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moral Stories 数据集处理
来源: https://huggingface.co/datasets/demelin/moral_stories
"""

import json
import os
from pathlib import Path
from tqdm import tqdm

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'


class MoralStoriesProcessor:
    """Moral Stories 数据处理器"""
    
    def __init__(self, output_dir="processed_data", max_len=4096, max_per_file=100000):
        self.output_dir = Path(output_dir)
        self.max_len = max_len
        self.max_per_file = max_per_file
        self.output_dir.mkdir(exist_ok=True)
        
    def format_record(self, record: dict) -> dict:
        """格式化单条记录为训练文本"""
        parts = []
        
        # 添加 ID
        record_id = record.get('ID', 'unknown')
        
        # 构建道德故事文本
        parts.append(f"【道德规范】{record.get('norm', '')}")
        parts.append(f"【情境】{record.get('situation', '')}")
        parts.append(f"【意图】{record.get('intention', '')}")
        parts.append(f"【道德行为】{record.get('moral_action', '')}")
        parts.append(f"【道德后果】{record.get('moral_consequence', '')}")
        parts.append(f"【不道德行为】{record.get('immoral_action', '')}")
        parts.append(f"【不道德后果】{record.get('immoral_consequence', '')}")
        
        text = '\n'.join(parts)
        
        # 截断
        if len(text) > self.max_len:
            text = text[:self.max_len]
        
        return {
            "id": f"openclaw_{record_id}",
            "text": text,
            "type": "moral_stories"
        }
    
    def process(self, input_file="moral_stories_full.jsonl"):
        """处理数据集"""
        print("=" * 60)
        print("📖 Moral Stories 数据集处理器")
        print("=" * 60)
        
        # 统计行数
        total = sum(1 for _ in open(input_file, 'r', encoding='utf-8'))
        print(f"📊 总条数: {total:,}")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
        print(f"📝 单文件最大条数: {self.max_per_file:,}")
        print("=" * 60)
        
        file_idx = 1
        batch = []
        processed = 0
        skipped = 0
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in tqdm(f, total=total, desc="处理进度"):
                if not line.strip():
                    continue
                    
                try:
                    record = json.loads(line.strip())
                except json.JSONDecodeError:
                    skipped += 1
                    continue
                
                # 格式化
                out_record = self.format_record(record)
                
                # 过滤空文本
                if len(out_record['text']) < 20:
                    skipped += 1
                    continue
                
                batch.append(out_record)
                processed += 1
                
                # 保存批次
                if len(batch) >= self.max_per_file:
                    self._save_batch(batch, file_idx)
                    batch = []
                    file_idx += 1
        
        # 保存剩余
        if batch:
            self._save_batch(batch, file_idx)
        else:
            file_idx -= 1
        
        # 输出统计
        print("\n" + "=" * 60)
        print("✅ 处理完成!")
        print("=" * 60)
        print(f"📊 原始样本: {total:,}")
        print(f"📊 有效样本: {processed:,}")
        print(f"📊 跳过样本: {skipped:,}")
        print(f"📁 生成文件: {file_idx}")
        
        print("\n📋 输出文件列表:")
        for f in sorted(self.output_dir.glob("moral_stories_part_*.jsonl")):
            size_mb = f.stat().st_size / (1024 * 1024)
            with open(f, 'r', encoding='utf-8') as fp:
                line_count = sum(1 for _ in fp)
            print(f"  • {f.name} ({size_mb:.2f} MB, {line_count:,} 条)")
        
        return {
            'original': total,
            'processed': processed,
            'skipped': skipped,
            'files': file_idx
        }
    
    def _save_batch(self, batch: list, idx: int):
        """保存一批数据"""
        path = self.output_dir / f"moral_stories_part_{idx:03d}.jsonl"
        with open(path, 'w', encoding='utf-8') as f:
            for r in batch:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f"  💾 {path.name} ({len(batch):,} 条)")


if __name__ == "__main__":
    p = MoralStoriesProcessor()
    p.process()

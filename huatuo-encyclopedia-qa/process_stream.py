#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Huatuo Encyclopedia QA 完整数据处理
使用 HF-Mirror 流式加载，分别处理 train/test/validation
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from datasets import load_dataset
from tqdm import tqdm


class HuatuoProcessor:
    """Huatuo Encyclopedia QA 数据处理器"""
    
    def __init__(self, output_dir="processed_data", max_len=4096, max_per_file=100000):
        self.output_dir = Path(output_dir)
        self.max_len = max_len
        self.max_per_file = max_per_file
        self.output_dir.mkdir(exist_ok=True)
        
    def load_split(self, split_name: str):
        """流式加载指定数据集划分"""
        print(f"\n⏳ 正在加载 {split_name} 数据集...")
        dataset = load_dataset(
            "FreedomIntelligence/huatuo_encyclopedia_qa",
            split=split_name
        )
        return dataset
    
    def format_record(self, record: Dict[str, Any]) -> str:
        """格式化单条记录为文本"""
        parts = []
        
        # 处理 questions
        if 'questions' in record and record['questions']:
            q_list = record['questions']
            if isinstance(q_list, list):
                flat_q = []
                for item in q_list:
                    if isinstance(item, list):
                        flat_q.extend(item)
                    else:
                        flat_q.append(item)
                q_text = '；'.join(str(x) for x in flat_q if x)
            else:
                q_text = str(q_list)
            parts.append(f"问题：{q_text}")
        
        # 处理 answers
        if 'answers' in record and record['answers']:
            a_list = record['answers']
            if isinstance(a_list, list):
                a_text = '；'.join(str(x) for x in a_list if x)
            else:
                a_text = str(a_list)
            parts.append(f"回答：{a_text}")
        
        return '\n'.join(parts)
    
    def process_split(self, split_name: str, dataset):
        """处理单个数据集划分"""
        print(f"\n{'='*60}")
        print(f"🔄 处理 {split_name} 数据集")
        print(f"{'='*60}")
        
        total = len(dataset)
        print(f"📊 总条数: {total:,}")
        
        file_idx = 1
        batch = []
        processed = 0
        skipped = 0
        
        for idx in tqdm(range(total), desc=f"处理 {split_name}"):
            try:
                record = dataset[idx]
                
                # 格式化文本
                text = self.format_record(record)
                
                # 截断
                if len(text) > self.max_len:
                    text = text[:self.max_len]
                
                # 过滤短文本
                if len(text) < 20:
                    skipped += 1
                    continue
                
                out_record = {
                    "id": f"openclaw_{split_name}_{processed:08d}",
                    "text": text,
                    "type": "medical_encyclopedia"
                }
                batch.append(out_record)
                processed += 1
                
                # 保存批次
                if len(batch) >= self.max_per_file:
                    self._save_batch(batch, split_name, file_idx)
                    batch = []
                    file_idx += 1
                    
            except Exception as e:
                print(f"\n⚠️  第 {idx} 条处理失败: {e}")
                skipped += 1
                continue
        
        # 保存剩余
        if batch:
            self._save_batch(batch, split_name, file_idx)
        else:
            file_idx -= 1
        
        print(f"\n✅ {split_name} 完成!")
        print(f"  原始: {total:,}")
        print(f"  有效: {processed:,}")
        print(f"  跳过: {skipped:,}")
        print(f"  文件: {file_idx}")
        
        return {
            'split': split_name,
            'original': total,
            'processed': processed,
            'skipped': skipped,
            'files': file_idx
        }
    
    def _save_batch(self, batch: list, split_name: str, idx: int):
        """保存一批数据"""
        path = self.output_dir / f"huatuo_{split_name}_part_{idx:03d}.jsonl"
        with open(path, 'w', encoding='utf-8') as f:
            for r in batch:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f"  💾 {path.name} ({len(batch):,} 条)")
    
    def process_all(self):
        """处理所有数据集划分"""
        print("🚀 Huatuo Encyclopedia QA 数据处理")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
        
        results = []
        splits = ['train', 'test', 'validation']
        
        for split in splits:
            dataset = self.load_split(split)
            result = self.process_split(split, dataset)
            results.append(result)
        
        # 总统计
        print("\n" + "="*60)
        print("📊 全部处理完成 - 汇总")
        print("="*60)
        for r in results:
            print(f"\n{r['split'].upper()}:")
            print(f"  原始: {r['original']:,}")
            print(f"  有效: {r['processed']:,}")
            print(f"  文件: {r['files']}")
        
        print("\n📋 输出文件列表:")
        for f in sorted(self.output_dir.glob("huatuo_*.jsonl")):
            size_mb = f.stat().st_size / (1024 * 1024)
            with open(f, 'r', encoding='utf-8') as fp:
                line_count = sum(1 for _ in fp)
            print(f"  • {f.name} ({size_mb:.2f} MB, {line_count:,} 条)")
        
        return results


if __name__ == "__main__":
    p = HuatuoProcessor()
    p.process_all()

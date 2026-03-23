#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载并处理完整的 Huatuo Encyclopedia QA train 数据集
使用 hf-mirror 加速
"""

import os
import json
import requests
from pathlib import Path
from tqdm import tqdm

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

DATA_URL = "https://hf-mirror.com/datasets/FreedomIntelligence/huatuo_encyclopedia_qa/resolve/main/train_datasets.jsonl"

class HuatuoFullProcessor:
    def __init__(self, output_dir="processed_data", max_len=4096, max_per_file=100000):
        self.output_dir = Path(output_dir)
        self.max_len = max_len
        self.max_per_file = max_per_file
        self.output_dir.mkdir(exist_ok=True)
        self.skipped = 0
        self.raw_file = self.output_dir / "train_datasets.jsonl"
        
    def download(self):
        """下载 train 数据集"""
        if self.raw_file.exists():
            print(f"✅ 文件已存在: {self.raw_file}")
            return
            
        print(f"⬇️  开始下载: {DATA_URL}")
        print("📦 预估大小: 576 MB")
        
        response = requests.get(DATA_URL, stream=True, timeout=300)
        total = int(response.headers.get('content-length', 0))
        
        with open(self.raw_file, 'wb') as f, tqdm(
            desc="train_datasets.jsonl",
            total=total,
            unit='B',
            unit_scale=True,
            unit_divisor=1024
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        print(f"✅ 下载完成: {self.raw_file}")
        
    def count_lines(self):
        """统计总行数"""
        print("📊 统计数据集大小...")
        count = 0
        with open(self.raw_file, 'r', encoding='utf-8') as f:
            for _ in tqdm(f, desc="计数"):
                count += 1
        print(f"📊 总行数: {count:,}")
        return count
        
    def process(self):
        """处理数据"""
        # 下载
        self.download()
        
        # 统计行数
        total = self.count_lines()
        
        # 处理
        file_idx = 1
        batch = []
        processed = 0
        
        print("\n🔄 开始处理数据...")
        with open(self.raw_file, 'r', encoding='utf-8') as f:
            for line in tqdm(f, total=total, desc="处理"):
                if not line.strip():
                    continue
                    
                try:
                    record = json.loads(line.strip())
                except json.JSONDecodeError:
                    self.skipped += 1
                    continue
                
                # 格式化文本
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
                
                text = '\n'.join(parts)
                
                # 截断
                if len(text) > self.max_len:
                    text = text[:self.max_len]
                
                # 过滤短文本
                if len(text) < 20:
                    self.skipped += 1
                    continue
                
                out_record = {
                    "id": f"openclaw_{processed:08d}",
                    "text": text,
                    "type": "medical_encyclopedia"
                }
                batch.append(out_record)
                processed += 1
                
                # 保存批次
                if len(batch) >= self.max_per_file:
                    self._save(batch, file_idx)
                    print(f"\n💾 已保存 huatuo_part_{file_idx:03d}.jsonl ({len(batch):,} 条)")
                    file_idx += 1
                    batch = []
        
        # 保存剩余
        if batch:
            self._save(batch, file_idx)
            print(f"\n💾 已保存 huatuo_part_{file_idx:03d}.jsonl ({len(batch):,} 条)")
        
        # 统计
        print("\n" + "="*60)
        print("✅ 处理完成!")
        print("="*60)
        print(f"📊 原始总行数: {total:,}")
        print(f"📊 有效数据: {processed:,}")
        print(f"📊 跳过: {self.skipped:,}")
        print(f"📁 输出文件数: {file_idx - 1}")
        
        # 列出输出文件
        print("\n📋 输出文件:")
        for f in sorted(self.output_dir.glob("huatuo_part_*.jsonl")):
            size_mb = f.stat().st_size / (1024 * 1024)
            with open(f, 'r', encoding='utf-8') as fp:
                line_count = sum(1 for _ in fp)
            print(f"  • {f.name} ({size_mb:.2f} MB, {line_count:,} 条)")
        
        return file_idx - 1, processed
        
    def _save(self, batch, idx):
        path = self.output_dir / f"huatuo_part_{idx:03d}.jsonl"
        with open(path, 'w', encoding='utf-8') as f:
            for r in batch:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')


if __name__ == "__main__":
    p = HuatuoFullProcessor()
    p.process()

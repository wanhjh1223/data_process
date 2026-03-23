#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Huatuo Encyclopedia QA 完整数据处理
分别处理 train / test / validation 三个数据集
"""

import json
import os
import requests
from pathlib import Path
from tqdm import tqdm

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

BASE_URL = "https://hf-mirror.com/datasets/FreedomIntelligence/huatuo_encyclopedia_qa/resolve/main"

DATASETS = {
    'train': {'file': 'train_datasets.jsonl', 'size_mb': 576},
    'test': {'file': 'test_datasets.jsonl', 'size_mb': 1.7},
    'validation': {'file': 'validation_datasets.jsonl', 'size_mb': 1.6}
}

class HuatuoCompleteProcessor:
    def __init__(self, output_dir="processed_data", max_len=4096, max_per_file=100000):
        self.output_dir = Path(output_dir)
        self.max_len = max_len
        self.max_per_file = max_per_file
        self.output_dir.mkdir(exist_ok=True)
        
    def download(self, split_name, file_name, size_mb):
        """下载指定数据集"""
        url = f"{BASE_URL}/{file_name}"
        raw_file = self.output_dir / file_name
        
        if raw_file.exists():
            print(f"✅ {split_name} 已存在，跳过下载")
            return raw_file
            
        print(f"\n⬇️  开始下载 {split_name}: {file_name}")
        print(f"📦 预估大小: {size_mb} MB")
        
        response = requests.get(url, stream=True, timeout=300)
        total = int(response.headers.get('content-length', 0))
        
        with open(raw_file, 'wb') as f, tqdm(
            desc=file_name,
            total=total,
            unit='B',
            unit_scale=True
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        print(f"✅ {split_name} 下载完成")
        return raw_file
    
    def process_split(self, split_name, raw_file):
        """处理单个数据集"""
        print(f"\n{'='*60}")
        print(f"🔄 处理 {split_name} 数据集")
        print(f"{'='*60}")
        
        # 统计行数
        print("📊 统计行数...")
        total_lines = sum(1 for _ in open(raw_file, 'r', encoding='utf-8'))
        print(f"📊 {split_name} 总行数: {total_lines:,}")
        
        # 处理
        file_idx = 1
        batch = []
        processed = 0
        skipped = 0
        
        with open(raw_file, 'r', encoding='utf-8') as f:
            for line in tqdm(f, total=total_lines, desc=f"处理 {split_name}"):
                if not line.strip():
                    continue
                    
                try:
                    record = json.loads(line.strip())
                except json.JSONDecodeError:
                    skipped += 1
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
                    self._save(batch, split_name, file_idx)
                    batch = []
                    file_idx += 1
        
        # 保存剩余
        if batch:
            self._save(batch, split_name, file_idx)
        else:
            file_idx -= 1
        
        # 统计
        print(f"\n✅ {split_name} 处理完成!")
        print(f"  原始: {total_lines:,}")
        print(f"  有效: {processed:,}")
        print(f"  跳过: {skipped:,}")
        print(f"  文件: {file_idx}")
        
        return {
            'split': split_name,
            'original': total_lines,
            'processed': processed,
            'skipped': skipped,
            'files': file_idx
        }
    
    def _save(self, batch, split_name, idx):
        """保存一批数据"""
        path = self.output_dir / f"huatuo_{split_name}_part_{idx:03d}.jsonl"
        with open(path, 'w', encoding='utf-8') as f:
            for r in batch:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f"  💾 {path.name} ({len(batch):,} 条)")
    
    def process_all(self):
        """处理所有数据集"""
        print("🚀 开始处理 Huatuo Encyclopedia QA 完整数据集")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
        
        results = []
        
        for split_name, info in DATASETS.items():
            # 下载
            raw_file = self.download(split_name, info['file'], info['size_mb'])
            # 处理
            result = self.process_split(split_name, raw_file)
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
    p = HuatuoCompleteProcessor()
    p.process_all()

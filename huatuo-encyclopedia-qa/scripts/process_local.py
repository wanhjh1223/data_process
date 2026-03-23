#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Huatuo Encyclopedia QA 数据集处理器
使用已下载的本地文件
"""

import json
from pathlib import Path
from tqdm import tqdm

class HuatuoProcessor:
    def __init__(self, output_dir="processed_data", max_len=4096, max_per_file=100000):
        self.output_dir = Path(output_dir)
        self.max_len = max_len
        self.max_per_file = max_per_file
        self.output_dir.mkdir(exist_ok=True)
        self.skipped = 0
        
    def load_jsonl(self, filepath):
        """加载 jsonl 文件"""
        records = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))
        return records
        
    def process(self):
        """处理数据"""
        data_dir = Path("./hf_data")
        
        # 查找所有 jsonl 文件
        jsonl_files = list(data_dir.glob("*.jsonl"))
        print(f"📁 找到 {len(jsonl_files)} 个 jsonl 文件")
        
        # 读取所有数据
        all_records = []
        for jf in jsonl_files:
            print(f"📖 读取: {jf.name}")
            records = self.load_jsonl(jf)
            print(f"   共 {len(records):,} 条")
            all_records.extend(records)
        
        total = len(all_records)
        print(f"\n📊 总数据量: {total:,}")
        
        # 查看第一条数据
        if all_records:
            print("\n📄 第一条数据示例:")
            print(f"  字段: {list(all_records[0].keys())}")
            for k, v in list(all_records[0].items())[:3]:
                preview = str(v)[:100] + "..." if len(str(v)) > 100 else str(v)
                print(f"  {k}: {preview}")
        
        # 处理并保存
        file_idx = 1
        batch = []
        
        print("\n🔄 开始处理数据...")
        for idx, record in tqdm(enumerate(all_records), total=total, desc="处理"):
            # 格式化文本
            parts = []
            
            # 处理 questions (可能是嵌套列表)
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
                "id": f"openclaw_{idx:08d}",
                "text": text,
                "type": "medical_encyclopedia"
            }
            batch.append(out_record)
            
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
        else:
            file_idx -= 1
        
        # 统计
        print("\n" + "="*60)
        print("✅ 处理完成!")
        print("="*60)
        print(f"📊 总数据: {total:,}")
        print(f"📊 有效数据: {total - self.skipped:,}")
        print(f"📊 跳过: {self.skipped:,}")
        print(f"📁 输出文件数: {file_idx}")
        
        # 列出输出文件
        print("\n📋 输出文件:")
        for f in sorted(self.output_dir.glob("*.jsonl")):
            size_mb = f.stat().st_size / (1024 * 1024)
            with open(f, 'r', encoding='utf-8') as fp:
                line_count = sum(1 for _ in fp)
            print(f"  • {f.name} ({size_mb:.2f} MB, {line_count:,} 条)")
        
        return file_idx, total - self.skipped
        
    def _save(self, batch, idx):
        path = self.output_dir / f"huatuo_part_{idx:03d}.jsonl"
        with open(path, 'w', encoding='utf-8') as f:
            for r in batch:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    p = HuatuoProcessor()
    p.process()

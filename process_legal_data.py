#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法律数据集处理脚本
处理 LawRefBook 和 CrimeKgAssitant
"""

import json
import os
import re
from pathlib import Path
from tqdm import tqdm

class LawDataProcessor:
    def __init__(self, output_dir="processed_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.max_per_file = 100000
        
    def process_crime_kg(self):
        """处理罪名知识图谱"""
        print("\n" + "="*60)
        print("📚 处理罪名知识图谱 (kg_crime.json)")
        print("="*60)
        
        input_file = "/root/.openclaw/workspace/data_process/crime_kg_assistant/data/kg_crime.json"
        
        batch = []
        file_idx = 1
        total = 0
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in tqdm(f, desc="处理罪名"):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    record = json.loads(line)
                    
                    # 构建文本
                    parts = []
                    parts.append(f"【罪名大类】{record.get('crime_big', '')}")
                    parts.append(f"【具体罪名】{record.get('crime_small', '')}")
                    
                    # 概念
                    if record.get('gainian'):
                        parts.append(f"【概念】{' '.join(record['gainian'])}")
                    
                    # 特征
                    if record.get('tezheng'):
                        parts.append(f"【构成要件】{' '.join(record['tezheng'])}")
                    
                    # 认定
                    if record.get('rending'):
                        parts.append(f"【认定】{' '.join(record['rending'])}")
                    
                    # 处罚
                    if record.get('chufa'):
                        parts.append(f"【处罚】{' '.join(record['chufa'])}")
                    
                    # 法条
                    if record.get('fatiao'):
                        parts.append(f"【法条】{' '.join(record['fatiao'])}")
                    
                    # 司法解释
                    if record.get('jieshi'):
                        parts.append(f"【司法解释】{' '.join(record['jieshi'])}")
                    
                    # 辩护
                    if record.get('bianhu'):
                        parts.append(f"【辩护要点】{' '.join(record['bianhu'])}")
                    
                    text = '\n'.join(parts)
                    
                    out_record = {
                        "id": f"crime_kg_{total:08d}",
                        "text": text,
                        "type": "crime_knowledge"
                    }
                    
                    batch.append(out_record)
                    total += 1
                    
                    if len(batch) >= self.max_per_file:
                        self._save(batch, "crime_kg", file_idx)
                        batch = []
                        file_idx += 1
                        
                except Exception as e:
                    continue
        
        if batch:
            self._save(batch, "crime_kg", file_idx)
        
        print(f"✅ 罪名知识图谱处理完成: {total} 条")
        return total
    
    def process_qa_corpus(self):
        """处理法务问答"""
        print("\n" + "="*60)
        print("💬 处理法务问答 (qa_corpus.json)")
        print("="*60)
        
        input_file = "/root/.openclaw/workspace/data_process/crime_kg_assistant/data/qa_corpus.json"
        
        batch = []
        file_idx = 1
        total = 0
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in tqdm(f, desc="处理问答"):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    record = json.loads(line)
                    
                    question = record.get('question', '')
                    answers = record.get('answers', [])
                    
                    if not question or not answers:
                        continue
                    
                    # 构建文本
                    if isinstance(answers, list):
                        answer_text = '\n'.join(answers)
                    else:
                        answer_text = str(answers)
                    
                    text = f"【问题】{question}\n【回答】{answer_text}"
                    
                    out_record = {
                        "id": f"legal_qa_{total:08d}",
                        "text": text,
                        "type": "legal_qa"
                    }
                    
                    batch.append(out_record)
                    total += 1
                    
                    if len(batch) >= self.max_per_file:
                        self._save(batch, "legal_qa", file_idx)
                        batch = []
                        file_idx += 1
                        
                except Exception as e:
                    continue
        
        if batch:
            self._save(batch, "legal_qa", file_idx)
        
        print(f"✅ 法务问答处理完成: {total} 条")
        return total
    
    def process_law_refbook(self):
        """处理法律法规"""
        print("\n" + "="*60)
        print("⚖️  处理法律法规 (LawRefBook)")
        print("="*60)
        
        base_dir = Path("/root/.openclaw/workspace/data_process/law_refbook")
        md_files = list(base_dir.rglob("*.md"))
        
        batch = []
        file_idx = 1
        total = 0
        
        for md_file in tqdm(md_files, desc="处理法律文件"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取文件名作为标题
                title = md_file.stem
                
                # 构建文本
                text = f"【法律名称】{title}\n\n{content}"
                
                out_record = {
                    "id": f"law_ref_{total:08d}",
                    "text": text,
                    "type": "law_regulation"
                }
                
                batch.append(out_record)
                total += 1
                
                if len(batch) >= self.max_per_file:
                    self._save(batch, "law_regulation", file_idx)
                    batch = []
                    file_idx += 1
                    
            except Exception as e:
                continue
        
        if batch:
            self._save(batch, "law_regulation", file_idx)
        
        print(f"✅ 法律法规处理完成: {total} 条")
        return total
    
    def _save(self, batch, data_type, idx):
        """保存一批数据"""
        path = self.output_dir / f"{data_type}_part_{idx:03d}.jsonl"
        with open(path, 'w', encoding='utf-8') as f:
            for r in batch:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f"  💾 {path.name} ({len(batch)} 条)")
    
    def process_all(self):
        """处理所有数据"""
        print("🚀 开始处理法律数据集")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
        
        results = {
            'crime_kg': self.process_crime_kg(),
            'legal_qa': self.process_qa_corpus(),
            'law_regulation': self.process_law_refbook()
        }
        
        # 总统计
        print("\n" + "="*60)
        print("📊 全部处理完成 - 汇总")
        print("="*60)
        
        total = 0
        for data_type, count in results.items():
            print(f"  {data_type}: {count:,} 条")
            total += count
        
        print(f"\n  总计: {total:,} 条")
        
        print("\n📋 输出文件列表:")
        for f in sorted(self.output_dir.glob("*.jsonl")):
            size_mb = f.stat().st_size / (1024 * 1024)
            with open(f, 'r', encoding='utf-8') as fp:
                line_count = sum(1 for _ in fp)
            print(f"  • {f.name} ({size_mb:.2f} MB, {line_count:,} 条)")
        
        return results

if __name__ == "__main__":
    p = LawDataProcessor()
    p.process_all()

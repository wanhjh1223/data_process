#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法务问答数据集处理脚本
处理 CrimeKgAssitant 数据集中的 qa_corpus.json

数据源: https://github.com/liuhuanyong/CrimeKgAssitant
数据量: 203,459条问答对
格式: JSONL (每条一问一答)
"""

import json
from pathlib import Path
from tqdm import tqdm

def process_legal_qa(max_per_file=100000):
    """处理法务问答"""
    input_file = Path(__file__).parent / "data" / "qa_corpus.json"
    
    print(f"💬 处理法务问答: {input_file}")
    
    batch = []
    file_idx = 1
    total = 0
    
    def save_batch():
        nonlocal batch, file_idx
        if not batch:
            return
        output_file = Path(__file__).parent / f"legal_qa_part_{file_idx:03d}.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for r in batch:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f"  💾 {output_file.name} ({len(batch)} 条)")
        batch = []
        file_idx += 1
    
    with open(input_file, 'r', encoding='utf-8') as f_in:
        for line in tqdm(f_in, desc="处理问答"):
            line = line.strip()
            if not line:
                continue
                
            try:
                record = json.loads(line)
                
                question = record.get('question', '')
                answers = record.get('answers', [])
                
                if not question or not answers:
                    continue
                
                # 构建回答文本
                if isinstance(answers, list):
                    answer_text = '\n'.join(answers)
                else:
                    answer_text = str(answers)
                
                out_record = {
                    "id": f"legal_qa_{total:08d}",
                    "question": question,
                    "answer": answer_text,
                    "text": f"【问题】{question}\n【回答】{answer_text}",
                    "type": "legal_qa"
                }
                
                batch.append(out_record)
                total += 1
                
                if len(batch) >= max_per_file:
                    save_batch()
                    
            except Exception as e:
                continue
    
    # 保存最后一批
    save_batch()
    
    print(f"✅ 处理完成: {total} 条")
    return total

if __name__ == "__main__":
    process_legal_qa()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
罪名知识图谱处理脚本
处理 CrimeKgAssitant 数据集中的 kg_crime.json

数据源: https://github.com/liuhuanyong/CrimeKgAssitant
数据量: 856条罪名知识
格式: JSONL (每条一个罪名)
"""

import json
from pathlib import Path
from tqdm import tqdm

def process_crime_kg():
    """处理罪名知识图谱"""
    input_file = Path(__file__).parent / "data" / "kg_crime.json"
    output_file = Path(__file__).parent / "crime_kg_part_001.jsonl"
    
    print(f"📚 处理罪名知识图谱: {input_file}")
    
    total = 0
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        
        for line in tqdm(f_in, desc="处理罪名"):
            line = line.strip()
            if not line:
                continue
                
            try:
                record = json.loads(line)
                
                # 构建文本
                parts = []
                parts.append(f"【罪名大类】{record.get('crime_big', '')}")
                parts.append(f"【具体罪名】{record.get('crime_small', '')}")
                
                if record.get('gainian'):
                    parts.append(f"【概念】{' '.join(record['gainian'])}")
                if record.get('tezheng'):
                    parts.append(f"【构成要件】{' '.join(record['tezheng'])}")
                if record.get('rending'):
                    parts.append(f"【认定】{' '.join(record['rending'])}")
                if record.get('chufa'):
                    parts.append(f"【处罚】{' '.join(record['chufa'])}")
                if record.get('fatiao'):
                    parts.append(f"【法条】{' '.join(record['fatiao'])}")
                if record.get('jieshi'):
                    parts.append(f"【司法解释】{' '.join(record['jieshi'])}")
                if record.get('bianhu'):
                    parts.append(f"【辩护要点】{' '.join(record['bianhu'])}")
                
                out_record = {
                    "id": f"crime_kg_{total:08d}",
                    "text": '\n'.join(parts),
                    "type": "crime_knowledge",
                    "crime_big": record.get('crime_big', ''),
                    "crime_small": record.get('crime_small', '')
                }
                
                f_out.write(json.dumps(out_record, ensure_ascii=False) + '\n')
                total += 1
                    
            except Exception as e:
                continue
    
    print(f"✅ 处理完成: {total} 条 -> {output_file}")
    return total

if __name__ == "__main__":
    process_crime_kg()

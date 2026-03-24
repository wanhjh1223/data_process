#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法律法规数据集处理脚本
处理 LawRefBook 法律条文数据

数据源: https://github.com/LawRefBook/Laws
数据量: 3,531条法律法规
格式: JSONL (每条一部法律/司法解释)
"""

import json
from pathlib import Path
from tqdm import tqdm

def process_law_regulation():
    """处理法律法规"""
    base_dir = Path(__file__).parent / "raw_data"
    output_file = Path(__file__).parent / "law_regulation_part_001.jsonl"
    
    # 递归查找所有 md 文件
    md_files = list(base_dir.rglob("*.md"))
    
    print(f"⚖️  处理法律法规: {len(md_files)} 个文件")
    
    total = 0
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for md_file in tqdm(md_files, desc="处理法律文件"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取文件名作为标题
                title = md_file.stem
                
                # 构建输出记录
                out_record = {
                    "id": f"law_reg_{total:08d}",
                    "title": title,
                    "text": f"【法律名称】{title}\n\n{content}",
                    "type": "law_regulation",
                    "category": md_file.parent.name,
                    "file_path": str(md_file.relative_to(base_dir))
                }
                
                f_out.write(json.dumps(out_record, ensure_ascii=False) + '\n')
                total += 1
                    
            except Exception as e:
                continue
    
    print(f"✅ 处理完成: {total} 条 -> {output_file}")
    return total

if __name__ == "__main__":
    process_law_regulation()

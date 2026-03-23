#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Huatuo Medical Knowledge Graph Preprocessing Script
处理 FreedomIntelligence/huatuo_knowledge_graph_qa 数据集
使用 HF-Mirror 镜像加速下载
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# 设置镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

try:
    from datasets import load_dataset
    from tqdm import tqdm
except ImportError as e:
    print(f"请先安装依赖: pip install datasets tqdm -q")
    sys.exit(1)


class MedicalDataProcessor:
    """医学知识图谱数据处理器"""
    
    def __init__(self, max_length: int = 4096, max_per_file: int = 100000):
        self.max_length = max_length
        self.max_per_file = max_per_file
        self.output_dir = Path("processed_data")
        self.output_dir.mkdir(exist_ok=True)
        self.processed_count = 0
        self.file_idx = 1
        self.current_batch = []
        
    def load_dataset_from_hf(self, dataset_name: str = "FreedomIntelligence/huatuo_knowledge_graph_qa"):
        """从 Hugging Face 加载数据集（使用镜像）"""
        print(f"🔄 正在从 hf-mirror.com 加载数据集: {dataset_name}")
        print("⏳ 这可能需要几分钟，请耐心等待...")
        
        try:
            # 尝试直接加载
            dataset = load_dataset(dataset_name)
            return dataset
        except Exception as e:
            print(f"⚠️  直接加载失败: {e}")
            print("🔄 尝试备用方式...")
            
            try:
                # 尝试只加载 train split
                dataset = load_dataset(dataset_name, split='train')
                return {'train': dataset}
            except Exception as e2:
                print(f"❌ 加载失败: {e2}")
                raise
    
    def truncate_text(self, text: str) -> str:
        """截断文本到最大长度"""
        if len(text) > self.max_length:
            return text[:self.max_length]
        return text
    
    def format_list_to_text(self, value) -> str:
        """将列表或字符串转换为纯文本"""
        if isinstance(value, list):
            # 如果是列表，用顿号连接所有元素
            return '；'.join(str(item) for item in value if item)
        elif isinstance(value, str):
            # 如果字符串看起来像列表，尝试解析
            if value.startswith('[') and value.endswith(']'):
                try:
                    import ast
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, list):
                        return '；'.join(str(item) for item in parsed if item)
                except:
                    pass
            return value
        return str(value)
    
    def format_record_to_text(self, record: Dict[str, Any]) -> str:
        """将记录格式化为文本"""
        parts = []
        
        # Huatuo数据集字段: questions (列表), answers (字符串/列表)
        if 'questions' in record and record['questions']:
            q_text = self.format_list_to_text(record['questions'])
            parts.append(f"问题：{q_text}")
        
        if 'answers' in record and record['answers']:
            a_text = self.format_list_to_text(record['answers'])
            parts.append(f"回答：{a_text}")
        
        # 其他可能的字段 (兼容其他数据集)
        if 'question' in record and record['question']:
            parts.append(f"问题：{record['question']}")
        
        if 'answer' in record and record['answer']:
            parts.append(f"回答：{record['answer']}")
            
        if 'knowledge' in record and record['knowledge']:
            parts.append(f"医学知识：{record['knowledge']}")
        
        return "\n".join(parts)
    
    def process_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """处理单条记录"""
        text = self.format_record_to_text(record)
        text = self.truncate_text(text)
        
        # 确定type
        data_type = "medical_kg"
        if 'type' in record and record['type']:
            data_type = str(record['type'])
        elif 'split' in record and record['split']:
            data_type = str(record['split'])
        
        result = {
            "id": self.processed_count,
            "text": text,
            "type": data_type
        }
        
        self.processed_count += 1
        return result
    
    def save_batch(self):
        """保存当前批次到文件"""
        if not self.current_batch:
            return
            
        output_file = self.output_dir / f"medical_data_part_{self.file_idx:03d}.jsonl"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in self.current_batch:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"✅ 已保存: {output_file.name} ({len(self.current_batch)} 条)")
        
        self.current_batch = []
        self.file_idx += 1
    
    def process(self):
        """主处理流程"""
        print("=" * 60)
        print("🏥 Huatuo 医学知识图谱数据处理器")
        print("=" * 60)
        
        # 加载数据集
        dataset = self.load_dataset_from_hf()
        
        # 获取数据
        if isinstance(dataset, dict):
            if 'train' in dataset:
                raw_data = dataset['train']
            else:
                raw_data = dataset[list(dataset.keys())[0]]
        else:
            raw_data = dataset
        
        total = len(raw_data)
        print(f"\n📊 数据集总条数: {total:,}")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
        print(f"📝 单文件最大条数: {self.max_per_file:,}")
        print(f"📏 最大上下文长度: {self.max_length}")
        print("=" * 60)
        
        # 显示第一条数据示例
        print("\n📄 第一条数据示例:")
        sample = raw_data[0]
        for k, v in sample.items():
            preview = str(v)[:100] + "..." if len(str(v)) > 100 else str(v)
            print(f"  {k}: {preview}")
        print("=" * 60)
        
        # 处理数据
        print("\n🔄 开始处理数据...")
        
        for idx in tqdm(range(total), desc="处理进度"):
            try:
                record = raw_data[idx]
                processed = self.process_record(record)
                
                # 过滤空文本
                if processed['text'].strip():
                    self.current_batch.append(processed)
                
                # 达到最大数量时保存
                if len(self.current_batch) >= self.max_per_file:
                    self.save_batch()
                    
            except Exception as e:
                print(f"\n⚠️  处理第 {idx} 条时出错: {e}")
                continue
        
        # 保存最后一批
        self.save_batch()
        
        # 输出统计
        print("\n" + "=" * 60)
        print("✅ 处理完成!")
        print("=" * 60)
        print(f"📊 总处理条数: {self.processed_count:,}")
        print(f"📁 输出文件数: {self.file_idx - 1}")
        print(f"📂 输出目录: {self.output_dir.absolute()}")
        
        # 列出输出文件
        print("\n📋 输出文件列表:")
        for f in sorted(self.output_dir.glob("*.jsonl")):
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  • {f.name} ({size_mb:.2f} MB)")
        
        print("=" * 60)


if __name__ == "__main__":
    processor = MedicalDataProcessor(
        max_length=4096,
        max_per_file=100000
    )
    processor.process()

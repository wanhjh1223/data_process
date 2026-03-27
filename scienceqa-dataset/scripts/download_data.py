#!/usr/bin/env python3
"""直接下载ScienceQA数据集parquet文件"""

import os
import sys
from huggingface_hub import hf_hub_download, list_repo_files
from pathlib import Path

REPO_ID = "derek-thomas/ScienceQA"
RAW_DIR = "./raw"

def download_dataset():
    os.makedirs(RAW_DIR, exist_ok=True)
    
    print(f"Listing files in {REPO_ID}...")
    
    try:
        # 列出所有文件
        files = list_repo_files(REPO_ID, repo_type="dataset")
        print(f"Found {len(files)} files")
        
        # 筛选parquet文件
        parquet_files = [f for f in files if f.endswith('.parquet')]
        print(f"Found {len(parquet_files)} parquet files")
        
        for file in parquet_files:
            print(f"\nDownloading: {file}")
            try:
                local_path = hf_hub_download(
                    repo_id=REPO_ID,
                    filename=file,
                    repo_type="dataset",
                    local_dir=RAW_DIR,
                    local_dir_use_symlinks=False,
                    resume_download=True
                )
                print(f"  ✓ Saved to: {local_path}")
                
                # 获取文件大小
                size = os.path.getsize(local_path)
                print(f"  Size: {size / 1024 / 1024:.2f} MB")
                
            except Exception as e:
                print(f"  ✗ Error downloading {file}: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_dataset()

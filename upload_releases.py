#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传文件到 GitHub Release
"""

import os
import sys
import json
import requests
from pathlib import Path

# GitHub 配置
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO = "wanhjh1223/data_process"

def create_release(tag, title, body):
    """创建 Release"""
    url = f"https://api.github.com/repos/{REPO}/releases"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "tag_name": tag,
        "name": title,
        "body": body
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"✅ Release {tag} 创建成功")
        return response.json()['upload_url'].replace("{?name,label}", "")
    elif response.status_code == 422:
        # Release 已存在，获取上传 URL
        print(f"⚠️ Release {tag} 已存在，获取上传 URL...")
        get_url = f"https://api.github.com/repos/{REPO}/releases/tags/{tag}"
        resp = requests.get(get_url, headers=headers)
        if resp.status_code == 200:
            return resp.json()['upload_url'].replace("{?name,label}", "")
    else:
        print(f"❌ 创建 Release 失败: {response.status_code} - {response.text}")
        return None

def upload_file(upload_url, file_path):
    """上传单个文件"""
    file_name = Path(file_path).name
    file_size = Path(file_path).stat().st_size
    
    print(f"  📤 上传 {file_name} ({file_size/1024/1024:.2f} MB)...")
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    with open(file_path, 'rb') as f:
        response = requests.post(
            f"{upload_url}?name={file_name}",
            headers=headers,
            data=f
        )
    
    if response.status_code == 201:
        print(f"  ✅ {file_name} 上传成功")
        return True
    else:
        print(f"  ❌ {file_name} 上传失败: {response.status_code}")
        return False

def main():
    if not GITHUB_TOKEN:
        print("❌ 请设置 GITHUB_TOKEN 环境变量")
        sys.exit(1)
    
    base_dir = Path("huatuo-encyclopedia-qa/processed_data")
    
    # 定义三个 release
    releases = [
        {
            "tag": "v1.0-train",
            "title": "Huatuo Encyclopedia QA - Train Dataset",
            "body": "训练集 (362,329条)\n- huatuo_train_part_001.jsonl (100,000条)\n- huatuo_train_part_002.jsonl (100,000条)\n- huatuo_train_part_003.jsonl (100,000条)\n- huatuo_train_part_004.jsonl (62,329条)",
            "files": sorted(base_dir.glob("huatuo_train_part_*.jsonl"))
        },
        {
            "tag": "v1.0-test", 
            "title": "Huatuo Encyclopedia QA - Test Dataset",
            "body": "测试集 (1,000条)\n- huatuo_test_part_001.jsonl",
            "files": sorted(base_dir.glob("huatuo_test_part_*.jsonl"))
        },
        {
            "tag": "v1.0-validation",
            "title": "Huatuo Encyclopedia QA - Validation Dataset", 
            "body": "验证集 (999条)\n- huatuo_validation_part_001.jsonl",
            "files": sorted(base_dir.glob("huatuo_validation_part_*.jsonl"))
        }
    ]
    
    for release in releases:
        print(f"\n{'='*60}")
        print(f"🔄 处理 Release: {release['tag']}")
        print(f"{'='*60}")
        
        # 创建 release
        upload_url = create_release(release['tag'], release['title'], release['body'])
        if not upload_url:
            continue
        
        # 上传文件
        for file_path in release['files']:
            upload_file(upload_url, str(file_path))
    
    print("\n✅ 全部完成!")

if __name__ == "__main__":
    main()

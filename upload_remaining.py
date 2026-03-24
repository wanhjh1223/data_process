#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继续上传剩余文件到 GitHub Release
"""

import os
import requests
from pathlib import Path

TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "wanhjh1223/data_process"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_release_id(tag):
    """获取 Release ID"""
    url = f"https://api.github.com/repos/{REPO}/releases/tags/{tag}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()['id']
    return None

def create_release(tag, title, body):
    """创建 Release"""
    url = f"https://api.github.com/repos/{REPO}/releases"
    data = {"tag_name": tag, "name": title, "body": body}
    resp = requests.post(url, headers=HEADERS, json=data)
    if resp.status_code == 201:
        print(f"✅ Release {tag} 创建成功")
        return resp.json()['id']
    elif resp.status_code == 422:
        print(f"⚠️ Release {tag} 已存在")
        return get_release_id(tag)
    else:
        print(f"❌ 创建失败: {resp.text}")
        return None

def upload_file(release_id, file_path):
    """上传文件"""
    file_name = Path(file_path).name
    file_size = Path(file_path).stat().st_size
    
    # 获取上传 URL
    url = f"https://api.github.com/repos/{REPO}/releases/{release_id}"
    resp = requests.get(url, headers=HEADERS)
    upload_url = resp.json()['upload_url'].replace("{?name,label}", "")
    
    print(f"📤 上传 {file_name} ({file_size/1024/1024:.1f}MB)...")
    
    # 检查是否已存在
    assets = resp.json().get('assets', [])
    for asset in assets:
        if asset['name'] == file_name:
            print(f"  ✅ {file_name} 已存在，跳过")
            return True
    
    # 上传
    headers = {"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}
    with open(file_path, 'rb') as f:
        resp = requests.post(f"{upload_url}?name={file_name}", headers=headers, data=f)
    
    if resp.status_code == 201:
        print(f"  ✅ {file_name} 上传成功")
        return True
    else:
        print(f"  ❌ {file_name} 失败: {resp.status_code}")
        return False

# 文件目录
base = Path("/root/.openclaw/workspace/data_process/huatuo-encyclopedia-qa/processed_data")

# 1. 继续上传 train 剩余文件
train_id = get_release_id("v1.0-train")
if train_id:
    print("="*60)
    print("🔄 继续上传 Train 文件...")
    for f in sorted(base.glob("huatuo_train_part_*.jsonl")):
        upload_file(train_id, str(f))

# 2. 创建并上传 test
print("\n" + "="*60)
print("🔄 处理 Test...")
test_id = create_release("v1.0-test", "Huatuo Encyclopedia QA - Test Dataset", 
                         "测试集 (1,000条)")
if test_id:
    for f in sorted(base.glob("huatuo_test_part_*.jsonl")):
        upload_file(test_id, str(f))

# 3. 创建并上传 validation
print("\n" + "="*60)
print("🔄 处理 Validation...")
val_id = create_release("v1.0-validation", "Huatuo Encyclopedia QA - Validation Dataset",
                        "验证集 (999条)")
if val_id:
    for f in sorted(base.glob("huatuo_validation_part_*.jsonl")):
        upload_file(val_id, str(f))

print("\n✅ 全部完成!")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传法律法规文件
"""

import requests
import os
from pathlib import Path

TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "wanhjh1223/data_process"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def upload_file(release_id, file_path):
    file_name = Path(file_path).name
    file_size = Path(file_path).stat().st_size
    
    # 获取 release 详情
    url = f"https://api.github.com/repos/{REPO}/releases/{release_id}"
    resp = requests.get(url, headers=HEADERS)
    upload_url = resp.json()['upload_url'].replace("{?name,label}", "")
    
    # 检查是否已存在
    for asset in resp.json().get('assets', []):
        if asset['name'] == file_name:
            print(f"✅ {file_name} 已存在")
            return True
    
    print(f"📤 上传 {file_name} ({file_size/1024/1024:.2f}MB)...")
    
    # 分片上传
    headers = {"Authorization": f"token {TOKEN}", "Content-Type": "application/octet-stream"}
    with open(file_path, 'rb') as f:
        resp = requests.post(f"{upload_url}?name={file_name}", headers=headers, data=f, timeout=600)
    
    if resp.status_code == 201:
        print(f"✅ {file_name} 上传成功")
        return True
    print(f"❌ 失败: {resp.status_code}, {resp.text[:200]}")
    return False

# 获取法律法规 release ID
url = f"https://api.github.com/repos/{REPO}/releases/tags/v1.0-legal-regulations"
resp = requests.get(url, headers=HEADERS)
release_id = resp.json().get('id')
print(f"Release ID: {release_id}")

# 上传
file_path = "/root/.openclaw/workspace/data_process/law_regulation/law_regulation_part_001.jsonl"
upload_file(release_id, file_path)

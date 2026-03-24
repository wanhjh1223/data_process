#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传法律数据 Release
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

def create_release(tag, title, body):
    url = f"https://api.github.com/repos/{REPO}/releases"
    data = {"tag_name": tag, "name": title, "body": body}
    resp = requests.post(url, headers=HEADERS, json=data)
    if resp.status_code == 201:
        print(f"✅ Release {tag} 创建成功")
        return resp.json()['id']
    elif resp.status_code == 422:
        print(f"⚠️ Release {tag} 已存在")
        get_url = f"https://api.github.com/repos/{REPO}/releases/tags/{tag}"
        return requests.get(get_url, headers=HEADERS).json()['id']
    return None

def upload_file(release_id, file_path):
    file_name = Path(file_path).name
    file_size = Path(file_path).stat().st_size
    
    url = f"https://api.github.com/repos/{REPO}/releases/{release_id}"
    resp = requests.get(url, headers=HEADERS)
    upload_url = resp.json()['upload_url'].replace("{?name,label}", "")
    
    # 检查是否已存在
    for asset in resp.json().get('assets', []):
        if asset['name'] == file_name:
            print(f"  ✅ {file_name} 已存在")
            return True
    
    print(f"  📤 上传 {file_name} ({file_size/1024/1024:.2f}MB)...")
    headers = {"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}
    with open(file_path, 'rb') as f:
        resp = requests.post(f"{upload_url}?name={file_name}", headers=headers, data=f)
    if resp.status_code == 201:
        print(f"  ✅ {file_name} 上传成功")
        return True
    print(f"  ❌ 失败: {resp.status_code}")
    return False

base = Path("/root/.openclaw/workspace/data_process")

# 1. 罪名知识图谱
print("="*60)
print("🔄 创建罪名知识图谱 Release...")
release_id = create_release(
    "v1.0-legal-crime-kg",
    "法律数据 - 罪名知识图谱",
    "856项罪名知识图谱\n\n来源: CrimeKgAssitant\n包含: 概念、构成要件、认定、处罚、法条、司法解释、辩护要点"
)
if release_id:
    upload_file(release_id, base / "crime_kg" / "crime_kg_part_001.jsonl")

# 2. 法务问答
print("\n" + "="*60)
print("🔄 创建法务问答 Release...")
release_id = create_release(
    "v1.0-legal-qa",
    "法律数据 - 法务问答",
    "203,459条法务问答\n\n来源: CrimeKgAssitant\n格式: 问题 + 回答"
)
if release_id:
    for f in sorted(base.glob("legal_qa/legal_qa_part_*.jsonl")):
        upload_file(release_id, str(f))

# 3. 法律法规
print("\n" + "="*60)
print("🔄 创建法律法规 Release...")
release_id = create_release(
    "v1.0-legal-regulations",
    "法律数据 - 法律法规",
    "3,531条法律法规\n\n来源: LawRefBook/Laws\n包含: 刑法、民法典、宪法、行政法、经济法等"
)
if release_id:
    upload_file(release_id, base / "law_regulation" / "law_regulation_part_001.jsonl")

print("\n✅ 全部完成!")

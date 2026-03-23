#!/usr/bin/env python3
import os
import json

INDEX_FILE = "index.json"
PACKAGES_DIR = "packages"
GLOBAL_DIR = "global"

# 读取现有 index.json
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index = json.load(f)
else:
    index = {"global_version": "1.0.0", "global": [], "packages": {}}

global_list = [
    f for f in os.listdir(GLOBAL_DIR) if os.path.isfile(os.path.join(GLOBAL_DIR, f))
]
if index.get("global") != global_list:
    index["global"] = global_list

# 更新 packages 列表
for pkg_name in os.listdir(PACKAGES_DIR):
    pkg_path = os.path.join(PACKAGES_DIR, pkg_name)
    if not os.path.isdir(pkg_path):
        continue
    # 找到所有 svg 文件（去掉 .svg 后缀）
    files = [os.path.splitext(f)[0] for f in os.listdir(pkg_path) if f.endswith(".svg")]

    # 保留 version 和 required，如果没有则初始化
    pkg_entry = index["packages"].get(pkg_name, {})
    version = pkg_entry.get("version", "0.1.0")
    required = pkg_entry.get("required", [])

    # 更新文件列表
    index["packages"][pkg_name] = {
        "version": version,
        "required": required,
        "files": files,
    }

# 写回 index.json
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

print("index.json 已更新")

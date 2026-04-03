#!/usr/bin/env python3
import sys
import json
import time
import hashlib
from pathlib import Path
from gen_manifest import build_manifest, sha256_file  # 使用原来的 manifest 构建函数

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
PACKAGES_DIR = ROOT / "packages"
GLOBAL_DIR = ROOT / "global"
OUTPUT = ROOT / "index.json"


def calc_global_version(items):
    """
    计算 global 版本，items 的 value 可以是 dict（有 sha256）或者字符串（文件夹 version）
    """
    h = hashlib.sha256()
    for name in sorted(items.keys()):
        h.update(name.encode())
        v = items[name]
        if isinstance(v, dict):
            # 散文件
            h.update(v["sha256"].encode())
        else:
            # 文件夹 version 字符串
            h.update(v.encode())
    return h.hexdigest()[:12]


def build_global():
    """
    global 下：
    - files: 原散文件
    - packages: 文件夹，生成精简 manifest（只保留 file/sha256/size）
    """
    files = {}
    packages = {}

    if not GLOBAL_DIR.exists():
        return {"version": "0", "files": {}, "packages": {}}

    for entry in GLOBAL_DIR.iterdir():
        if entry.is_file():
            files[entry.name] = {
                "sha256": sha256_file(entry),
                "size": entry.stat().st_size,
            }
        elif entry.is_dir():
            manifest = build_manifest(entry)
            # 精简处理：只保留 file / sha256 / size
            simple_files = {}
            for f in manifest["files"]:
                simple_files[f["file"]] = {"sha256": f["sha256"], "size": f["size"]}
            packages[entry.name] = {
                "version": manifest["version"],
                "files": simple_files,
            }

    combined = {
        **{k: v["sha256"] for k, v in files.items()},
        **{k: v["version"] for k, v in packages.items()},
    }
    version = calc_global_version(combined)

    return {"version": version, "files": files, "packages": packages}


def build_packages():
    pkgs = {}
    if not PACKAGES_DIR.exists():
        return pkgs

    for pkg_dir in PACKAGES_DIR.iterdir():
        if not pkg_dir.is_dir():
            continue
        manifest_file = pkg_dir / "manifest.json"
        if not manifest_file.exists():
            continue
        with open(manifest_file) as f:
            manifest = json.load(f)
        pkgs[pkg_dir.name] = {
            "version": manifest["version"],
            "manifest": f"packages/{pkg_dir.name}/manifest.json",
        }
    return pkgs


def main():
    index = {
        "repo_version": 1,
        "generated_at": int(time.time()),
        "global": build_global(),
        "packages": build_packages(),
    }

    with open(OUTPUT, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"index.json generated at {OUTPUT}")


if __name__ == "__main__":
    main()

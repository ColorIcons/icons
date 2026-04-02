#!/usr/bin/env python3
import sys
import json
import time
import hashlib
from pathlib import Path

# 根目录，可指定 CI 输出目录
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
PACKAGES_DIR = ROOT / "packages"
GLOBAL_DIR = ROOT / "global"
OUTPUT = ROOT / "index.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def build_global():
    files = {}
    if not GLOBAL_DIR.exists():
        return {"version": "0", "files": {}}

    for f in GLOBAL_DIR.iterdir():
        if not f.is_file():
            continue
        files[f.name] = {
            "sha256": sha256_file(f),
            "size": f.stat().st_size,
        }

    version = calc_global_version(files)
    return {
        "version": version,
        "files": files,
    }


def calc_global_version(files):
    h = hashlib.sha256()
    for name in sorted(files.keys()):
        h.update(name.encode())
        h.update(files[name]["sha256"].encode())
    return h.hexdigest()[:12]


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

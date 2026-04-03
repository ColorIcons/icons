#!/usr/bin/env python3

import sys
import json
import hashlib
import re
from pathlib import Path

PACKAGES_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else "packages")

OPTIONAL_FILES = {
    "mat.png",
    "monochrome.png",
    "recbg.png",
    "recfg.png",
    "rec_night.png",
}

VARIANT_MAP = {
    "mat.png": ("icon", "mat"),
    "monochrome.png": ("icon", "monochrome"),
    "recbg.png": ("icon", "light"),
    "recfg.png": ("icon", "light"),
    "rec_night.png": ("icon", "dark"),
}

SIZE_SUFFIX_RE = re.compile(r"^\d+x\d+$")


def normalize_name(name: str) -> str:
    """
    将带尺寸的文件名归一化：
    recbg_1x2.png -> recbg.png
    monochrome_2x1.png -> monochrome.png
    """
    stem = Path(name).stem
    parts = stem.split("_")

    if len(parts) >= 2 and SIZE_SUFFIX_RE.match(parts[-1]):
        base = "_".join(parts[:-1])
    else:
        base = stem

    return f"{base}.png"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def detect_variant(name: str):
    base_name = normalize_name(name)
    return VARIANT_MAP.get(base_name, ("asset", None))


def is_required(name: str) -> bool:
    base_name = normalize_name(name)
    return base_name not in OPTIONAL_FILES


def calc_version_from_dir(pkg_dir: Path) -> str:
    """目录级 version，只在目录内容变化时更新"""
    h = hashlib.sha256()
    files = []

    for f in pkg_dir.iterdir():
        if not f.is_file():
            continue
        if f.name == "manifest.json":
            continue
        if f.suffix not in [".png"]:
            continue
        files.append(f)

    for f in sorted(files, key=lambda x: x.name):
        h.update(f.name.encode())
        with open(f, "rb") as fp:
            while chunk := fp.read(8192):
                h.update(chunk)

    return h.hexdigest()[:12]


def build_manifest(pkg_dir: Path):
    files = []

    for file in pkg_dir.iterdir():
        if not file.is_file():
            continue
        if file.name == "manifest.json":
            continue
        if file.suffix not in [".png"]:
            continue

        file_type, variant = detect_variant(file.name)

        entry = {
            "file": file.name,
            "type": file_type,
            "required": is_required(file.name),
            "sha256": sha256_file(file),
            "size": file.stat().st_size,
        }

        if variant:
            entry["variant"] = variant

        files.append(entry)

    manifest = {
        "version": calc_version_from_dir(pkg_dir),
        "files": sorted(files, key=lambda x: x["file"]),
    }

    return manifest


def main():
    if not PACKAGES_DIR.exists():
        print("packages directory not found")
        return

    for pkg_dir in PACKAGES_DIR.iterdir():
        if not pkg_dir.is_dir():
            continue

        print(f"Generating manifest for {pkg_dir.name}")
        manifest = build_manifest(pkg_dir)

        out_file = pkg_dir / "manifest.json"
        with open(out_file, "w") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import sys
import json
import time
import hashlib
import re
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
PACKAGES_DIR = ROOT / "packages"
GLOBAL_DIR = ROOT / "global"
OUTPUT = ROOT / "index.json"

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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def normalize_name(name: str) -> str:
    stem = Path(name).stem
    parts = stem.split("_")

    if len(parts) >= 2 and SIZE_SUFFIX_RE.match(parts[-1]):
        base = "_".join(parts[:-1])
    else:
        base = stem

    return f"{base}.png"


def detect_variant(name: str):
    base_name = normalize_name(name)
    return VARIANT_MAP.get(base_name, ("asset", None))


def is_required(name: str) -> bool:
    base_name = normalize_name(name)
    return base_name not in OPTIONAL_FILES


def build_package(pkg_dir: Path):
    files = []
    h = hashlib.sha256()

    file_list = []

    for file in pkg_dir.iterdir():
        if not file.is_file():
            continue
        if file.suffix != ".png":
            continue

        file_list.append(file)

    for file in sorted(file_list, key=lambda x: x.name):
        file_type, variant = detect_variant(file.name)

        sha = sha256_file(file)
        size = file.stat().st_size

        entry = {
            "file": file.name,
            "sha256": sha,
            "size": size,
            "type": file_type,
            "required": is_required(file.name),
        }

        if variant:
            entry["variant"] = variant

        files.append(entry)

        h.update(file.name.encode())
        h.update(sha.encode())

    version = h.hexdigest()[:12]

    return version, files


def calc_global_version(items):
    h = hashlib.sha256()
    for name in sorted(items.keys()):
        h.update(name.encode())
        v = items[name]
        if isinstance(v, dict):
            h.update(v["sha256"].encode())
        else:
            h.update(v.encode())
    return h.hexdigest()[:12]


def build_global():
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
            version, file_list = build_package(entry)

            simple_files = {
                f["file"]: {
                    "sha256": f["sha256"],
                    "size": f["size"],
                }
                for f in file_list
            }

            packages[entry.name] = {
                "version": version,
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

        version, file_list = build_package(pkg_dir)

        files = {}
        for f in file_list:
            entry = {
                "sha256": f["sha256"],
                "size": f["size"],
                "type": f["type"],
                "required": f["required"],
            }
            if "variant" in f:
                entry["variant"] = f["variant"]

            files[f["file"]] = entry

        pkgs[pkg_dir.name] = {
            "version": version,
            "count": len(files),
            "files": files,
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
        json.dump(index, f, separators=(",", ":"), ensure_ascii=False)

    print(f"index.json generated at {OUTPUT}")


if __name__ == "__main__":
    main()

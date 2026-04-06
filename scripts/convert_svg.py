#!/usr/bin/env python3

import base64
import subprocess
import sys
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_WORKERS = 16
TMP_ROOT = Path(".tmp_optimized")

stats = {"total": 0, "ok": 0, "skip": 0, "err": 0}


def zopflipng_compress(src: Path, dst: Path):
    """
    尝试用 zopflipng 压缩
    失败则 fallback 原图
    """
    result = subprocess.run(
        ["zopflipng", "-m", str(src), str(dst)],
        # stdout=subprocess.DEVNULL,
        # stderr=subprocess.DEVNULL,
    )

    if result.returncode in (0, 1) and dst.exists():
        return dst

    print(f"[WARN] fallback to original: {src}")
    return src


def png_to_svg(png_path: Path, svg_path: Path):
    with Image.open(png_path) as img:
        width, height = img.size

    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<image href="data:image/png;base64,{b64}" width="{width}" height="{height}"/>
</svg>"""

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)


def process_one(png_file: Path, root: Path):
    rel = png_file.relative_to(root)
    svg_file = png_file.with_suffix(".svg")
    tmp_png = TMP_ROOT / rel

    if svg_file.exists():
        return ("skip", rel)

    tmp_png.parent.mkdir(parents=True, exist_ok=True)

    try:
        optimized = zopflipng_compress(png_file, tmp_png)

        png_to_svg(optimized, svg_file)

        if svg_file.exists() and svg_file.stat().st_size > 0:
            png_file.unlink(missing_ok=True)

        if optimized != png_file:
            tmp_png.unlink(missing_ok=True)

        return ("ok", rel)

    except Exception as e:
        return ("err", f"{rel} ({e})")


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <target_dir>")
        return

    root = Path(sys.argv[1]).resolve()

    if not root.exists():
        print("[FATAL] Directory not found.")
        return

    TMP_ROOT.mkdir(parents=True, exist_ok=True)

    png_files = [p for p in root.rglob("*") if p.suffix.lower() == ".png"]

    if not png_files:
        print("[INFO] No PNG files found.")
        return

    stats["total"] = len(png_files)

    print(f"[INFO] Found {stats['total']} PNG files")
    print(f"[INFO] Using {MAX_WORKERS} threads")
    print("-" * 50)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(process_one, p, root) for p in png_files]

        for future in as_completed(futures):
            status, msg = future.result()

            if status == "ok":
                stats["ok"] += 1
                print(f"[OK]   {msg}")
            elif status == "skip":
                stats["skip"] += 1
                print(f"[SKIP] {msg}")
            else:
                stats["err"] += 1
                print(f"[ERR]  {msg}")

    print("-" * 50)
    print("[SUMMARY]")
    print(f"  Total : {stats['total']}")
    print(f"  OK    : {stats['ok']}")
    print(f"  Skip  : {stats['skip']}")
    print(f"  Error : {stats['err']}")

    import shutil

    shutil.rmtree(TMP_ROOT, ignore_errors=True)


if __name__ == "__main__":
    main()

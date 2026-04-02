#!/usr/bin/env python3

import sys
import json
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
INDEX_FILE = ROOT / "index.json"
OUTPUT_HTML = ROOT / "index.html"


def main():
    if not INDEX_FILE.exists():
        print(f"{INDEX_FILE} not found")
        return

    with open(INDEX_FILE) as f:
        index = json.load(f)

    html_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head><meta charset='UTF-8'><title>UX Icons</title>",
        "<style>",
        "body{font-family:sans-serif;padding:1em;} ",
        ".pkg{margin-bottom:2em;} ",
        ".pkg h2{margin:0.5em 0;} ",
        ".files{display:flex;flex-wrap:wrap;} ",
        ".file{margin:0.5em;text-align:center;width:100px;} ",
        "img{width:64px;height:64px;border:1px solid #ccc;padding:2px;cursor:pointer;} ",
        "a{text-decoration:none;color:inherit;}",
        ".meta{font-size:0.8em;color:#555;}</style>",
        "</head><body>",
        f"<h1>UX Icons Packages (repo version: {index.get('repo_version', '?')})</h1>",
        f"<p>Global version: {index.get('global', {}).get('version', '?')}</p>",
    ]

    for pkg_name, pkg_info in sorted(index.get("packages", {}).items()):
        manifest_path = ROOT / pkg_info["manifest"]
        if not manifest_path.exists():
            continue

        with open(manifest_path) as mf:
            manifest = json.load(mf)

        html_lines.append("<div class='pkg'>")
        html_lines.append(
            f"<h2>{pkg_name} (version: {manifest.get('version', '?')})</h2>"
        )
        html_lines.append("<div class='files'>")

        for f in manifest["files"]:
            file_path = f"{pkg_info['manifest'].rsplit('/', 1)[0]}/{f['file']}"
            meta_info = f"size: {f.get('size', '?')}B<br>sha256: {f.get('sha256', '?')[:12]}{'...' if len(f.get('sha256', '')) > 12 else ''}"
            if f.get("type") == "icon":
                html_lines.append(
                    f"<div class='file'><a href='{file_path}' target='_blank'><img src='{file_path}' alt='{f['file']}'></a><div class='meta'>{meta_info}</div><div>{f['file']}</div></div>"
                )
            else:
                html_lines.append(
                    f"<div class='file'><a href='{file_path}' target='_blank'>{f['file']}</a><div class='meta'>{meta_info}</div></div>"
                )

        html_lines.append("</div></div>")

    html_lines.append("</body></html>")

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"HTML preview generated at {OUTPUT_HTML}")


if __name__ == "__main__":
    main()

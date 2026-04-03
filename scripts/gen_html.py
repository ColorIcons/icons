#!/usr/bin/env python3

import sys
import json
import re
import time
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
INDEX_FILE = ROOT / "index.json"
OUTPUT_HTML = ROOT / "index.html"

BUILD_ID = int(time.time())

STYLE = """
:root { 
    --body-bg: #ffffff;
    --text-main: #24292f;
    --text-muted: #57606a;
    --bg-subtle: #f6f8fa; 
    --border-color: #d0d7de; 
    --primary: #0969da; 
    --version-bg: #ddf4ff;
    --version-text: #0969da;
    --card-bg: #f6f8fa;
    --img-container-bg: #ffffff;
    --monochrome-fixed-bg: #f0f0f0; 
}

[data-theme="dark"] {
    --body-bg: #0d1117;
    --text-main: #c9d1d9;
    --text-muted: #8b949e;
    --bg-subtle: #161b22; 
    --border-color: #30363d; 
    --primary: #58a6ff; 
    --version-bg: rgba(56, 139, 253, 0.15);
    --version-text: #58a6ff;
    --card-bg: #161b22;
    --img-container-bg: #0d1117;
}

body { 
    font-family: -apple-system, system-ui, sans-serif; 
    padding: 15px; background: var(--body-bg); color: var(--text-main); 
    margin: 0; transition: background 0.2s, color 0.2s;
}

.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; gap: 10px; flex-wrap: wrap; }
h1 { font-size: 1.5rem; margin: 0; }

.theme-toggle {
    padding: 8px 16px; border-radius: 20px; border: 1px solid var(--border-color);
    background: var(--bg-subtle); color: var(--text-main); cursor: pointer; font-size: 14px; white-space: nowrap;
}

.search-container { 
    position: sticky; top: 0; background: var(--body-bg); 
    padding: 15px 0; z-index: 100; border-bottom: 1px solid var(--border-color); 
    margin-bottom: 20px; display: flex;
}

#search-input { 
    flex: 1; padding: 12px; border: 1px solid var(--border-color); 
    border-radius: 8px; background: var(--bg-subtle);
    color: var(--text-main); outline: none; font-size: 14px;
}

h2 { 
    display: flex; align-items: flex-start; justify-content: flex-start;
    margin-top: 2em; font-size: 1.2rem; border-bottom: 2px solid var(--border-color); 
    padding-bottom: 8px; gap: 12px;
}

.pkg-name { word-break: break-all; overflow-wrap: anywhere; flex: 1; line-height: 1.4; }
.pkg-version { 
    padding: 2px 10px; font-size: 0.75rem; background: var(--version-bg); 
    color: var(--version-text); border-radius: 12px; flex-shrink: 0;
    white-space: nowrap; margin-top: 4px;
}

.files { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }

.file-card { 
    border: 1px solid var(--border-color); border-radius: 12px; padding: 15px; 
    display: flex; flex-direction: column; background: var(--card-bg); 
    min-height: 280px; box-sizing: border-box;
}

.img-wrapper { flex-grow: 1; display: flex; align-items: center; justify-content: center; min-height: 210px; }

.img-container { 
    position: relative; width: 64px; height: 64px; 
    border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; 
    display: flex; align-items: center; justify-content: center; 
    background: var(--img-container-bg);
}
.img-container img { position: absolute; width: 100%; height: 100%; object-fit: contain; }

.size-1x2 { width: 60px; height: 205px; } 
.size-2x1 { width: 205px; height: 60px; }
.size-2x2 { width: 205px; height: 205px; }

.special-container { border: 1.5px solid var(--primary); }
.night-bg { background: radial-gradient(circle, #202020 0%, #292929 100%); border-color: #444; }
.monochrome-bg { background-color: var(--monochrome-fixed-bg) !important; border-color: #ccc; }

.card-footer { margin-top: 12px; text-align: center; border-top: 1px dashed var(--border-color); padding-top: 10px; }
.filename { font-size: 12px; font-weight: 600; color: var(--text-main); word-break: break-all; }
.meta { font-size: 10px; color: var(--text-muted); margin-top: 4px; }
"""

SCRIPTS = """
<script>
const toggleBtn = document.getElementById('theme-toggle');
const htmlEl = document.documentElement;
const updateThemeUI = (theme) => {
    htmlEl.setAttribute('data-theme', theme);
    toggleBtn.innerText = theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
    localStorage.setItem('preview-theme', theme);
};
const savedTheme = localStorage.getItem('preview-theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
updateThemeUI(savedTheme);
toggleBtn.addEventListener('click', () => {
    const isDark = htmlEl.getAttribute('data-theme') === 'dark';
    updateThemeUI(isDark ? 'light' : 'dark');
});
document.getElementById('search-input').addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    document.querySelectorAll('.pkg-section').forEach(section => {
        const pkgName = section.getAttribute('data-pkg').toLowerCase();
        section.style.display = pkgName.includes(term) ? 'block' : 'none';
    });
});
</script>
"""


def get_grid_class(filename):
    match = re.search(r"_(\d)x(\d)", filename)
    return f"size-{match.group(1)}x{match.group(2)}" if match else ""


def get_suffix(filename, prefix):
    return filename.replace(prefix, "").replace(".png", "")


def main():
    if not INDEX_FILE.exists():
        print(f"Error: {INDEX_FILE} not found")
        return

    with open(INDEX_FILE) as f:
        index = json.load(f)

    raw_pkgs = index.get("packages", {})
    global_pkgs = index.get("global", {}).get("packages", {})
    all_packages = {**raw_pkgs, **global_pkgs}

    html_lines = [
        "<!DOCTYPE html><html>",
        f"<head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>UX Icons Preview</title><style>{STYLE}</style></head><body>",
        "<div class='header-row'><h1>UX Icons Preview</h1><button id='theme-toggle' class='theme-toggle'>🌙 Dark Mode</button></div>",
        '<div class="search-container"><input type="text" id="search-input" placeholder="Search packages..."></div>',
    ]

    for pkg_name, pkg_info in sorted(all_packages.items()):
        files_list = []

        if "manifest" in pkg_info:
            manifest_path = ROOT / pkg_info["manifest"]
            if not manifest_path.exists():
                continue
            with open(manifest_path) as mf:
                manifest = json.load(mf)
            pkg_version = manifest.get("version", "0.0.1")
            pkg_dir = pkg_info["manifest"].rsplit("/", 1)[0]
            files_list = manifest.get("files", [])
        else:
            pkg_version = pkg_info.get("version", "Global")
            pkg_dir = f"global/{pkg_name}"
            raw_files = pkg_info.get("files", {})
            for f_name, f_data in raw_files.items():
                files_list.append({"file": f_name, "size": f_data.get("size", 0)})

        html_lines.append(f"<div class='pkg-section' data-pkg='{pkg_name}'>")
        html_lines.append(
            f"<h2><span class='pkg-name'>{pkg_name}</span><span class='pkg-version'>v{pkg_version}</span></h2><div class='files'>"
        )

        skip_files, display_items = set(), []

        fgs = [f for f in files_list if f["file"].startswith("recfg")]
        for fg in fgs:
            suffix = get_suffix(fg["file"], "recfg")
            bg_name = f"recbg{suffix}.png"
            bg = next((f for f in files_list if f["file"] == bg_name), None)
            if bg:
                display_items.append(
                    {
                        "type": "light-pair",
                        "files": [bg, fg],
                        "name": f"light{suffix}",
                        "meta": "Layered",
                    }
                )
                skip_files.update([fg["file"], bg_name])
            else:
                skip_files.add(fg["file"])

        nights = [f for f in files_list if f["file"].startswith("rec_night")]
        for n in nights:
            suffix = get_suffix(n["file"], "rec_night")
            display_items.append(
                {
                    "type": "night-mode",
                    "file": n,
                    "name": f"night{suffix}",
                    "meta": "Night Mode",
                }
            )
            skip_files.add(n["file"])

        for f in files_list:
            if f["file"] in skip_files or f["file"].startswith("recbg"):
                continue
            display_items.append(
                {
                    "type": "single",
                    "data": f,
                    "name": f["file"],
                    "meta": f"{f.get('size', 0)} B",
                }
            )

        for item in display_items:
            is_monochrome = "monochrome" in item["name"].lower()
            mono_cls = "monochrome-bg" if is_monochrome else ""

            if item["type"] == "light-pair":
                grid_cls = get_grid_class(item["files"][1]["file"])
                img_html = f"""<div class='img-container special-container {grid_cls} {mono_cls}'>
                                <img src='{pkg_dir}/{item["files"][0]["file"]}?v={BUILD_ID}' style='z-index:1'>
                                <img src='{pkg_dir}/{item["files"][1]["file"]}?v={BUILD_ID}' style='z-index:2'>
                              </div>"""
            elif item["type"] == "night-mode":
                grid_cls = get_grid_class(item["file"]["file"])
                img_html = f"""<div class='img-container special-container night-bg {grid_cls}'>
                                <img src='{pkg_dir}/{item["file"]["file"]}?v={BUILD_ID}' style='z-index:2'>
                              </div>"""
            else:
                grid_cls = get_grid_class(item["data"]["file"])
                f_name = item["data"]["file"]
                if f_name.lower().endswith((".png", ".jpg", ".svg", ".webp")):
                    content = f"<img src='{pkg_dir}/{f_name}?v={BUILD_ID}'>"
                else:
                    content = "📄"
                img_html = (
                    f"<div class='img-container {grid_cls} {mono_cls}'>{content}</div>"
                )

            html_lines.append(f"""
            <div class='file-card'>
                <div class='img-wrapper'>{img_html}</div>
                <div class='card-footer'>
                    <div class='filename'>{item["name"]}</div>
                    <div class='meta'>{item["meta"]}</div>
                </div>
            </div>""")

        html_lines.append("</div></div>")

    html_lines.append(SCRIPTS)
    html_lines.append("</body></html>")

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))
    print(f"Preview generated: {OUTPUT_HTML} (Total: {len(all_packages)} packages)")


if __name__ == "__main__":
    main()

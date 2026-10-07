"""Shared look for every SVG: palette, font stack, terminal-window chrome."""

import os
from xml.sax.saxutils import escape

STATIC = os.environ.get("STATIC") == "1"  # frozen frame for local previews

BG = "#0d1117"
CHROME = "#161b22"
BORDER = "#30363d"
FG = "#c9d1d9"
MUTED = "#8b949e"
DIM = "#484f58"
ACCENT = "#39d353"
AMBER = "#f0b429"

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def window(width: int, height: int, title: str, body: str, style: str = "") -> str:
    """Wrap body in a rounded terminal window with a title bar (30px tall)."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{FONT}">
<style>{style}</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 30 V10.5 a10 10 0 0 1 10 -10 H{width - 10.5} a10 10 0 0 1 10 10 V30 Z" fill="{CHROME}"/>
<line x1="0.5" y1="30" x2="{width - 0.5}" y2="30" stroke="{BORDER}"/>
<circle cx="18" cy="15.5" r="5" fill="#ff5f57"/><circle cx="34" cy="15.5" r="5" fill="#febc2e"/><circle cx="50" cy="15.5" r="5" fill="#28c840"/>
<text x="{width / 2}" y="19.5" text-anchor="middle" font-size="11.5" fill="{MUTED}">{escape(title)}</text>
{body}
</svg>
"""


def write(path: str, svg: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print(f"wrote {path} ({len(svg) / 1024:.1f} KB)")

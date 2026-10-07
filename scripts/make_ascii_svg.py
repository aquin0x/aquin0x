"""Image -> monochrome ASCII SVG that prints itself row by row (SMIL, plays once).

    python scripts/make_ascii_svg.py                 # uses assets/source-prepped.png, else assets/source.png
    python scripts/make_ascii_svg.py path/to/img.png
"""

import os
import sys

import numpy as np
from PIL import Image, ImageOps

from _theme import ACCENT, AMBER, FG, MUTED, STATIC, window, write

ROOT = os.path.join(os.path.dirname(__file__), "..")
W, H = 370, 420  # same height as info-card.svg so the two sit flush side by side
COLS = 60
RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space clears the background
CHAR_W, LINE_H = 0.6, 1.18  # monospace advance and line height, in em


def load(path: str) -> Image.Image:
    img = Image.open(path)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGBA", img.size, "white")
        img = Image.alpha_composite(bg, img)
    gray = ImageOps.autocontrast(img.convert("L"), cutoff=1)
    bbox = ImageOps.invert(gray).getbbox()  # crop surplus white margin
    return gray.crop(bbox) if bbox else gray


def to_rows(gray: Image.Image, area_w: float, area_h: float) -> tuple[list[str], float]:
    cw = area_w / COLS
    fs = cw / CHAR_W
    rows = int(round(COLS * gray.height / gray.width * CHAR_W / LINE_H))
    max_rows = int(area_h // (fs * LINE_H))
    if rows > max_rows:  # tall image: shrink the grid instead of overflowing
        rows = max_rows
    px = np.asarray(gray.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    idx = np.clip(((1.0 - px) * len(RAMP)).astype(int), 0, len(RAMP) - 1)
    return ["".join(RAMP[i] for i in r).rstrip() for r in idx], fs


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else next(
        p for p in (os.path.join(ROOT, "assets", n) for n in ("source-prepped.png", "source.png")) if os.path.exists(p)
    )
    pad, top, foot = 20, 30 + 44, 46
    area_w, area_h = W - 2 * pad, H - top - foot
    rows, fs = to_rows(load(src), area_w, area_h)
    lh, cw = fs * LINE_H, fs * CHAR_W
    y_first = top + (area_h - len(rows) * lh) / 2 + fs

    defs, text = [], []
    step, dur = 0.07, 0.32
    for i, row in enumerate(rows):
        if not row.strip():
            continue
        y = y_first + i * lh
        tl = f' textLength="{len(row) * cw:.2f}" lengthAdjust="spacing"'
        line = f'<text x="{pad}" y="{y:.2f}" xml:space="preserve"{tl}>{row}</text>'
        if STATIC:
            text.append(line)
            continue
        b = 0.5 + i * step
        rw = len(row) * cw
        defs.append(
            f'<clipPath id="r{i}"><rect x="{pad}" y="{y - fs:.2f}" width="0" height="{lh + 1:.2f}">'
            f'<animate attributeName="width" from="0" to="{rw:.1f}" begin="{b:.2f}s" dur="{dur}s" fill="freeze"/></rect></clipPath>'
        )
        text.append(
            f'<g clip-path="url(#r{i})">{line}</g>'
            f'<rect x="{pad}" y="{y - fs * 0.85:.2f}" width="{cw:.2f}" height="{fs:.2f}" fill="{ACCENT}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{b:.2f}s"/>'
            f'<animate attributeName="x" from="{pad}" to="{pad + rw:.1f}" begin="{b:.2f}s" dur="{dur}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{b + dur:.2f}s"/></rect>'
        )
    done = 0.5 + len(rows) * step + dur

    caret = "" if STATIC else (
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" begin="{done:.2f}s" repeatCount="indefinite"/>'
    )
    body = f"""
<text x="{pad}" y="58" font-size="13"><tspan fill="{AMBER}">aquin0x@github</tspan><tspan fill="{MUTED}"> ~ $ </tspan><tspan fill="{FG}">whoami</tspan></text>
<defs>{''.join(defs)}</defs>
<g font-size="{fs:.2f}" fill="{FG}">{''.join(text)}</g>
<text x="{pad}" y="{H - 18}" font-size="13"><tspan fill="{AMBER}">aquin0x@github</tspan><tspan fill="{MUTED}"> ~ $ </tspan></text>
<rect x="{pad + 19 * 7.8:.1f}" y="{H - 29}" width="8" height="14" fill="{ACCENT}" opacity="{0 if not STATIC else 1}">
<set attributeName="opacity" to="1" begin="{done:.2f}s"/>{caret}</rect>
"""
    write(os.path.join(ROOT, "aquin0x-ascii.svg"), window(W, H, "~/portrait.txt", body))


if __name__ == "__main__":
    main()

"""data/contributions.json -> contrib-heatmap.svg (53x7 grid, diagonal reveal, plays once)."""

import json
import os
from datetime import date

from _theme import ACCENT, AMBER, DIM, FG, MUTED, STATIC, window, write

ROOT = os.path.join(os.path.dirname(__file__), "..")
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 = neon top end for the busiest days)

W, H = 860, 248
CELL, GAP = 11, 3
STEP = CELL + GAP
LABEL_W = 30


def level5_threshold(days: list[dict]) -> int:
    counts = sorted(d["count"] for d in days if d["count"])
    return counts[int(len(counts) * 0.9)] if counts else 1


def main() -> None:
    with open(os.path.join(ROOT, "data", "contributions.json"), encoding="utf-8") as f:
        data = json.load(f)
    days = data["days"]
    start = date.fromisoformat(days[0]["date"])
    start_sun = start.toordinal() - (start.weekday() + 1) % 7  # grid columns start on Sunday
    weeks = (date.fromisoformat(days[-1]["date"]).toordinal() - start_sun) // 7 + 1

    x0 = (W - (LABEL_W + weeks * STEP - GAP)) / 2 + LABEL_W
    y0 = 102
    hot = level5_threshold(days)

    cells, months_seen = [], []
    for d in days:
        dt = date.fromisoformat(d["date"])
        col, row = (dt.toordinal() - start_sun) // 7, (dt.weekday() + 1) % 7
        lvl = 5 if d["level"] == 4 and d["count"] >= hot else min(d["level"], 4)
        x, y = x0 + col * STEP, y0 + row * STEP
        delay = 0.55 + (col + row) * 0.022
        cells.append(
            f'<rect class="c" x="{x:.1f}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s">'
            f'<title>{d["count"]} on {d["date"]}</title></rect>'
        )
        if dt.day <= 7 and row == 0 and col < weeks - 1:
            months_seen.append((col, dt.strftime("%b")))

    month_labels = "".join(
        f'<text x="{x0 + c * STEP:.1f}" y="{y0 - 8}" font-size="10.5" fill="{MUTED}">{m}</text>'
        for c, m in months_seen
    )
    day_labels = "".join(
        f'<text x="{x0 - 8:.1f}" y="{y0 + r * STEP + 9}" font-size="10" fill="{MUTED}" text-anchor="end">{n}</text>'
        for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )

    grid_right = x0 + weeks * STEP - GAP
    legend_y = y0 + 7 * STEP + 16
    legend = "".join(
        f'<rect x="{grid_right - 40 - (6 - i) * STEP:.1f}" y="{legend_y - 9}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )
    legend += (
        f'<text x="{grid_right - 44 - 6 * STEP:.1f}" y="{legend_y}" font-size="10.5" fill="{MUTED}" text-anchor="end">Less</text>'
        f'<text x="{grid_right - 36:.1f}" y="{legend_y}" font-size="10.5" fill="{MUTED}">More</text>'
    )

    best = data["best_day"]
    best_label = date.fromisoformat(best["date"]).strftime("%b %d").replace(" 0", " ")
    stats = [
        (f'{data["total"]:,}', "contributions in the last year"),
        (str(data["current_streak"]), "day streak"),
        (str(data["longest_streak"]), "longest"),
        (str(best["count"]), f"best day ({best_label})"),
    ]
    tspans = f'<tspan fill="{DIM}">  ·  </tspan>'.join(
        f'<tspan fill="{ACCENT}" font-weight="700">{v}</tspan><tspan fill="{FG}"> {k}</tspan>' for v, k in stats
    )

    body = f"""
<text class="ln" x="{x0 - LABEL_W:.1f}" y="58" font-size="13"><tspan fill="{AMBER}">aquin0x@github</tspan><tspan fill="{MUTED}"> ~ $ </tspan><tspan fill="{FG}">./contributions.sh --last-year</tspan></text>
{month_labels}{day_labels}
{''.join(cells)}
<g class="ft">{legend}
<text x="{x0 - LABEL_W:.1f}" y="{legend_y}" font-size="11.5">{tspans}</text></g>
"""
    end = 0.55 + (weeks + 6) * 0.022 + 0.45
    style = "" if STATIC else f"""
.ln{{animation:in .5s ease-out .15s both}}
.c{{transform-box:fill-box;transform-origin:center;animation:drop .45s cubic-bezier(.2,.8,.3,1.2) both}}
.ft{{animation:in .6s ease-out {end:.2f}s both}}
@keyframes drop{{from{{opacity:0;transform:translateY(-9px) scale(.4)}}to{{opacity:1;transform:none}}}}
@keyframes in{{from{{opacity:0}}to{{opacity:1}}}}
"""
    svg = window(W, H, "contributions — aquin0x", body, style)
    write(os.path.join(ROOT, "contrib-heatmap.svg"), svg)


if __name__ == "__main__":
    main()

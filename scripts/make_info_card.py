"""Hand-authored neofetch-style card -> info-card.svg. Edit CONTENT and re-run."""

import os
from xml.sax.saxutils import escape

from _theme import ACCENT, AMBER, DIM, FG, MUTED, STATIC, window, write

ROOT = os.path.join(os.path.dirname(__file__), "..")
W, H = 490, 460

USER = "aquin0x"
HOST = "github"
CONTENT = [
    ("Name", "Alperen Sevinç"),
    ("Role", "Software & AI Engineer"),
    ("Loc", "Istanbul, TR"),
    ("Edu", "Karabük Univ. — Computer Engineering"),
    ("Prev", "Orjin · Eriklabs"),
    ("Lab", "Frax Labs — frax.tr"),
    ("Now", "Agent Office — 12 AI agents, one shared board"),
    ("Ships", "Haslet · Filom · Aymira · VİRA · LeadPin"),
    ("Front", "React · Next.js · Astro · Three.js · Tailwind"),
    ("Mobile", "Expo / React Native · Flutter"),
    ("Back", "Node · Hono · Drizzle · Prisma · PostgreSQL"),
    ("AI", "Gemini · Ollama · agents · automation"),
    ("Ops", "Coolify · Docker · Vercel · Tauri · Electron"),
    ("X", "@aqu1nox"),
]
SWATCHES = ["#484f58", "#ff7b72", "#39d353", "#f0b429", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]


def main() -> None:
    x, y, lh = 24, 62, 21
    lines = [
        f'<text x="{x}" y="{y}" font-size="13"><tspan fill="{AMBER}">{USER}@{HOST}</tspan>'
        f'<tspan fill="{MUTED}"> ~ $ </tspan><tspan fill="{FG}">neofetch</tspan></text>',
        f'<text x="{x}" y="{y + 31}" font-size="15" font-weight="700"><tspan fill="{ACCENT}">{USER}</tspan>'
        f'<tspan fill="{FG}">@</tspan><tspan fill="{ACCENT}">{HOST}</tspan></text>',
        f'<text x="{x}" y="{y + 49}" font-size="13" fill="{DIM}">{"─" * 22}</text>',
    ]
    for i, (k, v) in enumerate(CONTENT):
        ty = y + 72 + lh * i
        lines.append(
            f'<text x="{x}" y="{ty}" font-size="13"><tspan fill="{ACCENT}" font-weight="700">{escape(k)}</tspan>'
            f'<tspan x="{x + 64}" fill="{FG}">{escape(v)}</tspan></text>'
        )
    sw_y = y + 72 + lh * len(CONTENT) - 4
    lines.append("<g>" + "".join(
        f'<rect x="{x + i * 26}" y="{sw_y}" width="22" height="12" rx="2" fill="{c}"/>' for i, c in enumerate(SWATCHES)
    ) + "</g>")

    body = "\n".join(
        f'<g class="l" style="animation-delay:{0.35 + i * 0.1:.2f}s">{ln}</g>' for i, ln in enumerate(lines)
    )
    style = "" if STATIC else """
.l{animation:type .45s ease-out both}
@keyframes type{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}
"""
    write(os.path.join(ROOT, "info-card.svg"), window(W, H, f"{USER}@{HOST}: ~", body, style))


if __name__ == "__main__":
    main()

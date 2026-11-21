"""Render the Laurel rustle spinner as an animated PNG from the likeness SVG.

uv run --no-project --with cairosvg --with pillow python make-laurel-spinner.py <laurel.svg> <outdir>
"""

import base64
import io
import math
import re
import sys
from pathlib import Path

import cairosvg
from PIL import Image

SIZE = 80
FRAMES = 30
FRAME_MS = 33
SWAY_DEG = 24
LEAF_ORDER = [1, 2, 3, 4, 5]  # clockwise from top right
SMILE = '<path d="M89.48 99.7Q96 105.87 102.52 99.7"/>'

src = Path(sys.argv[1]).read_text()
out = Path(sys.argv[2])

pivots = {
    int(m.group(1)): m.group(2).split()
    for m in re.finditer(r'id="leaf-(\d)" class="leaf" data-pivot="([^"]+)"', src)
}

# Transparent background, filled bloom so the cream face reads on light themes too.
base = re.sub(r'<rect id="bg"[^>]*/>', "", src)
base = re.sub(r' style="transform-box:view-box;transform-origin:[^"]+"', "", base)
base = base.replace('fill="none" stroke-linecap="round" stroke-linejoin="round"/>\n<g id="face"',
                    'fill="#2E5E4E" stroke-linecap="round" stroke-linejoin="round"/>\n<g id="face"')
base = base.replace('<g id="mouth"></g>', f'<g id="mouth">{SMILE}</g>')
base = base.replace('viewBox="0 0 192 192"', 'viewBox="40 54 112 112"')
assert 'fill="#2E5E4E"' in base and SMILE in base


def frame(t):
    svg = base
    for i, (px, py) in pivots.items():
        deg = SWAY_DEG * math.sin(2 * math.pi * (t - LEAF_ORDER.index(i) / 5))
        svg = svg.replace(f'id="leaf-{i}" class="leaf"',
                          f'id="leaf-{i}" class="leaf" transform="rotate({deg:.2f} {px} {py})"')
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=SIZE, output_height=SIZE)
    return Image.open(io.BytesIO(png)).convert("RGBA")


frames = [frame(k / FRAMES) for k in range(FRAMES)]
out.mkdir(parents=True, exist_ok=True)
apng = out / "laurel-spinner.png"
frames[0].save(apng, save_all=True, append_images=frames[1:], duration=FRAME_MS, loop=0,
               disposal=1, blend=0, optimize=True)

b64 = base64.b64encode(apng.read_bytes()).decode()
cards = "".join(
    f'<div class="c" style="background:{bg};color:{fg};border-color:{bd}">'
    f'<p>Laurel is working… <i style="width:20px;height:20px;vertical-align:middle;margin-left:4px"></i></p>'
    f'<p><i style="width:96px;height:96px"></i></p></div>'
    for bg, fg, bd in [("#0d1117", "#e6edf3", "#30363d"), ("#ffffff", "#1f2328", "#d1d9e0")])
(out / "preview.html").write_text(f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Laurel Spinner</title>
<style>body{{font:15px -apple-system,Segoe UI,sans-serif;background:#f6f8fa;margin:0;padding:16px}}
.row{{display:flex;gap:12px;flex-wrap:wrap}}.c{{border:1px solid;border-radius:6px;padding:4px 16px;min-width:240px}}
i{{display:inline-block;background:url(data:image/png;base64,{b64}) center/contain no-repeat}}</style>
</head><body><div class="row">{cards}</div></body></html>""")
print(apng, apng.stat().st_size, "bytes")

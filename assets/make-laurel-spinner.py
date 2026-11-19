"""Render Laurel spinner variants as looping GIFs from the real likeness SVG."""

import io
import math
import re
import sys
from pathlib import Path

import cairosvg
from PIL import Image

SRC = Path(sys.argv[1]).read_text()
OUT = Path(sys.argv[2])
SIZE = 48
CENTER = (96.0, 94.6)
LEAF_ORDER = [1, 2, 3, 4, 5]  # clockwise from top right

PIVOTS = {
    int(m.group(1)): tuple(map(float, m.group(2).split()))
    for m in re.finditer(r'id="leaf-(\d)" class="leaf" data-pivot="([^"]+)"', SRC)
}


def base_svg():
    s = SRC.replace('<rect id="bg" width="192" height="192" fill="#2E5E4E"/>',
                    '<circle cx="96" cy="100" r="62" fill="#2E5E4E"/>')
    s = re.sub(r' style="transform-box:view-box;transform-origin:[^"]+"', "", s)
    s = s.replace('<g id="mouth"></g>', '<g id="mouth"><path d="M89.48 99.7Q96 105.87 102.52 99.7"/></g>')
    return s.replace('viewBox="0 0 192 192"', 'viewBox="34 38 124 124" width="124" height="124"')


BASE = base_svg()


def with_leaf_transforms(fn):
    s = BASE
    for i, (px, py) in PIVOTS.items():
        t = fn(i, px, py)
        s = s.replace(f'id="leaf-{i}" class="leaf"', f'id="leaf-{i}" class="leaf" transform="{t}"')
    return s


def chase(t):
    def fn(i, px, py):
        phase = (t - LEAF_ORDER.index(i) / 5) % 1
        k = max(0.0, math.cos(2 * math.pi * phase)) ** 4
        sc = 1 + 0.35 * k
        return f"translate({px} {py}) scale({sc}) translate({-px} {-py})"
    return with_leaf_transforms(fn)


def orbit(t):
    cx, cy = CENTER
    return BASE.replace('<g id="leaves" mask="url(#laurel-gap)"',
                        f'<g id="leaves" mask="url(#laurel-gap)"><g transform="rotate({360 * t} {cx} {cy})"') \
               .replace('</g>\n<g id="bloom"', '</g></g>\n<g id="bloom"')


def rustle(t):
    def fn(i, px, py):
        phase = t - LEAF_ORDER.index(i) / 5
        return f"rotate({24 * math.sin(2 * math.pi * phase)} {px} {py})"
    return with_leaf_transforms(fn)


def frame(svg):
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=SIZE, output_height=SIZE)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def save_gif(name, frames, ms):
    pal = []
    for im in frames:
        alpha = im.getchannel("A").point(lambda a: 255 if a >= 128 else 0)
        p = im.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT)
        p.paste(255, mask=Image.eval(alpha, lambda a: 255 - a))
        pal.append(p)
    pal[0].save(OUT / f"{name}.gif", save_all=True, append_images=pal[1:], duration=ms,
                loop=0, transparency=255, disposal=2, optimize=False)


VARIANTS = {"chase": (chase, 25, 40), "orbit": (orbit, 50, 40), "rustle": (rustle, 25, 40)}

OUT.mkdir(parents=True, exist_ok=True)
for name, (fn, n, ms) in VARIANTS.items():
    frames = [frame(fn(k / n)) for k in range(n)]
    save_gif(name, frames, ms)
    strip = Image.new("RGBA", (SIZE * 6, SIZE), (13, 17, 23, 255))
    for j, k in enumerate(range(0, n, max(1, n // 6))):
        if j < 6:
            strip.alpha_composite(frames[k], (j * SIZE, 0))
    strip.convert("RGB").resize((SIZE * 12, SIZE * 2), Image.NEAREST).save(OUT / f"{name}-strip.png")
    print(name, n, "frames")


import base64


def card(name, theme):
    bg, fg, border = ("#0d1117", "#e6edf3", "#30363d") if theme == "dark" else ("#ffffff", "#1f2328", "#d1d9e0")
    return (f'<div class="c" style="background:{bg};color:{fg};border-color:{border}">'
            f'<p>Laurel is working… <i class="g-{name}" style="width:14px;height:14px;vertical-align:middle;margin-left:4px"></i></p>'
            f'<p class="big"><i class="g-{name}" style="width:72px;height:72px"></i></p></div>')


gif_css = "".join(
    f".g-{n}{{background-image:url(data:image/gif;base64,{base64.b64encode((OUT / f'{n}.gif').read_bytes()).decode()})}}"
    for n in VARIANTS)
rows = "".join(
    f'<section><h2>{n}</h2><div class="row">{card(n, "dark")}{card(n, "light")}</div></section>'
    for n in VARIANTS)
(OUT / "preview.html").write_text(f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Laurel Spinner Options</title>
<style>body{{font:15px -apple-system,Segoe UI,sans-serif;background:#f6f8fa;color:#1f2328;margin:0;padding:16px}}
h2{{font-size:16px;margin:20px 0 8px}}.row{{display:flex;gap:12px;flex-wrap:wrap}}
.c{{border:1px solid;border-radius:6px;padding:4px 16px;min-width:240px}}.big{{margin:4px 0 12px}}
i{{display:inline-block;background-size:contain;background-repeat:no-repeat}}{gif_css}</style>
</head><body><h1 style="font-size:20px">Laurel spinner options</h1>{rows}</body></html>""")
print("preview written")

"""Render the RAG-poisoning figures in both themes.

One composition, two sizes: a 534x404 hero (matches the CVE post's hero) and a
1200x630 social card. The figure is the article's central measurement — where
each poisoned payload lands against the clean corpus range.

Layout is measured, not guessed: every block is sized from real font metrics
and anchored to the top or bottom of the frame, so nothing can overflow.

Run from the repo root:  python3 _rag_fig.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
FDIR = ROOT / "fonts"
OUT = ROOT / "rag-poisoning"

PALETTES = {
    "dark": dict(
        bg=(10, 10, 10), ink=(234, 234, 234), mute=(138, 138, 138),
        dim=(96, 96, 96), red=(230, 25, 25), line=(42, 42, 42),
        band=(34, 34, 34), label=(196, 196, 192),
    ),
    "light": dict(
        bg=(244, 244, 240), ink=(10, 10, 10), mute=(95, 95, 92),
        dim=(140, 140, 136), red=(196, 20, 20), line=(210, 208, 202),
        band=(229, 228, 222), label=(52, 52, 50),
    ),
}

# measured values, from the article
CLEAN_LO, CLEAN_HI = 20.4, 84.7
CLEAN_MEAN = 42.6
PAYLOADS = [("bias", 77.2, True), ("injection", 96.8, False), ("leakage", 115.8, False)]
SCALE_MAX = 130.0


def font(name, size):
    return ImageFont.truetype(str(FDIR / name), max(1, int(round(size))))


def text_h(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[3] - b[1]


def render(w, h, palette, s, compact=False):
    """s is the layout scale; compact drops the legend for thumbnail legibility."""
    c = PALETTES[palette]
    img = Image.new("RGB", (w, h), c["bg"])
    d = ImageDraw.Draw(img)

    pad = int(30 * s)
    d.rectangle([0, 0, w - 1, h - 1], outline=c["line"], width=max(1, int(s)))

    fs = 1.18 if compact else 1.0
    f_lab = font("JetBrainsMono-Regular.ttf", 10.5 * s * fs)
    f_small = font("JetBrainsMono-Regular.ttf", 9 * s * fs)
    f_big = font("ArchivoBlack-Regular.ttf", 18 * s)

    # ── header, top-anchored ──
    y = pad
    d.text((pad, y), "PERPLEXITY vs CLEAN CORPUS", font=f_lab, fill=c["label"])
    y += text_h(d, "PERPLEXITY", f_lab) + int(7 * s)
    if compact:
        d.text((pad, y), "15 clean docs · 3 payloads", font=f_small, fill=c["dim"])
        head_bottom = y + text_h(d, "15", f_small)
    else:
        d.text((pad, y), "GPT-2 · 15 clean documents · 3 payloads", font=f_small, fill=c["dim"])
        y += text_h(d, "GPT-2", f_small) + int(14 * s)

        # legend row, so the plot itself carries no floating labels
        lh = text_h(d, "x", f_small)
        sw = int(11 * s)
        d.rectangle([pad, y + lh // 2 - int(2 * s), pad + sw, y + lh // 2 + int(2 * s)],
                    fill=c["band"], outline=c["line"], width=max(1, int(s)))
        d.text((pad + sw + int(7 * s), y), "clean range 20–85", font=f_small, fill=c["mute"])
        lx2 = pad + sw + int(7 * s) + d.textlength("clean range 20–85", font=f_small) + int(18 * s)
        d.line([lx2, y, lx2, y + lh], fill=c["dim"], width=max(1, int(s)))
        d.text((lx2 + int(7 * s), y), "mean 42.6", font=f_small, fill=c["dim"])
        head_bottom = y + lh

    # ── caption, bottom-anchored ──
    cap2 = "no threshold admits every clean doc and rejects it"
    cap1_h = text_h(d, "bias", f_big)
    cap2_h = text_h(d, "bias", f_small)
    cap_y = h - pad - cap1_h - int(9 * s) - cap2_h
    d.text((pad, cap_y), "bias sits inside the clean range", font=f_big, fill=c["ink"])
    d.text((pad, cap_y + cap1_h + int(9 * s)), cap2, font=f_small, fill=c["mute"])

    # ── plot, fills the gap ──
    top = head_bottom + int(30 * s)
    axis_y = cap_y - int(30 * s)
    x0, x1 = pad, w - pad
    span = x1 - x0

    def X(v):
        return x0 + (min(v, SCALE_MAX) / SCALE_MAX) * span

    # clean range band — labelled in the legend, so the plot stays clean
    d.rectangle([X(CLEAN_LO), top, X(CLEAN_HI), axis_y], fill=c["band"])
    for v in (CLEAN_LO, CLEAN_HI):
        d.line([X(v), top, X(v), axis_y], fill=c["line"], width=max(1, int(s)))

    # mean marker
    mx = X(CLEAN_MEAN)
    d.line([mx, top, mx, axis_y], fill=c["dim"], width=max(1, int(s)))

    # baseline + ticks
    d.line([x0, axis_y, x1, axis_y], fill=c["line"], width=max(1, int(s)))
    for v in (0, 40, 80, 120):
        tx = X(v)
        d.line([tx, axis_y, tx, axis_y + int(5 * s)], fill=c["line"], width=max(1, int(s)))
        tw = d.textlength(str(v), font=f_small)
        d.text((min(tx - tw / 2, x1 - tw), axis_y + int(11 * s)),
               str(v), font=f_small, fill=c["dim"])

    # payload stems — labels stack into rows when they would collide
    lh_s = text_h(d, "x", f_small)
    row_y = {}
    for name, val, highlight in PAYLOADS:
        col = c["red"] if highlight else c["mute"]
        x = X(val)
        stem_top = top + int(26 * s)
        d.line([x, stem_top, x, axis_y], fill=col, width=max(2, int(2 * s)))
        cap = int(4 * s)
        d.rectangle([x - cap, stem_top - cap, x + cap, stem_top + cap], fill=col)

        tw = d.textlength(name, font=f_small)
        lx = min(max(x - tw / 2, pad), x1 - tw)
        # find the first row where this label clears every label already placed
        row = 0
        while True:
            clash = False
            for (olx, otw), orow in row_y.items():
                if orow == row and lx < olx + otw + int(10 * s) and olx < lx + tw + int(10 * s):
                    clash = True
                    break
            if not clash:
                break
            row += 1
        row_y[(lx, tw)] = row
        d.text((lx, stem_top - cap - lh_s - int(7 * s) - row * (lh_s + int(4 * s))),
               name, font=f_small, fill=col)

    return img


for theme in ("dark", "light"):
    hero = render(534, 404, theme, 1.42, compact=True)
    hero.save(OUT / ("hero.png" if theme == "dark" else "hero-light.png"))
    card = render(1200, 630, theme, 2.2)
    card.save(OUT / ("card.png" if theme == "dark" else "card-light.png"))
    print(f"{theme}: hero 534x404, card 1200x630")

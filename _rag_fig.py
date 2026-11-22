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
        band=(38, 38, 38), redband=(48, 22, 22), overlap=(78, 24, 24),
        label=(196, 196, 192),
    ),
    "light": dict(
        bg=(244, 244, 240), ink=(10, 10, 10), mute=(95, 95, 92),
        dim=(140, 140, 136), red=(196, 20, 20), line=(210, 208, 202),
        band=(228, 227, 221), redband=(246, 226, 224), overlap=(238, 190, 186),
        label=(52, 52, 50),
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
    d.text((pad, y), "GPT-2 PERPLEXITY, CLEAN vs POISONED", font=f_lab, fill=c["label"])
    y += text_h(d, "GPT-2", f_lab) + int(7 * s)
    if compact:
        d.text((pad, y), "15 clean docs · 3 payloads", font=f_small, fill=c["dim"])
        head_bottom = y + text_h(d, "15", f_small)
    else:
        d.text((pad, y), "the clean and poisoned ranges share an interval", font=f_small, fill=c["dim"])
        head_bottom = y + text_h(d, "the", f_small)

    # ── caption, bottom-anchored ──
    cap2 = ("77.2 – 84.7 is shared by both" if compact
            else "no threshold admits every clean doc and rejects every payload")
    cap1_h = text_h(d, "bias", f_big)
    cap2_h = text_h(d, "bias", f_small)
    cap_y = h - pad - cap1_h - int(9 * s) - cap2_h
    d.text((pad, cap_y), "the two ranges overlap", font=f_big, fill=c["ink"])
    d.text((pad, cap_y + cap1_h + int(9 * s)), cap2, font=f_small, fill=c["mute"])

    # ── plot: two distributions, with the shared interval shaded ──
    x0, x1 = pad, w - pad
    span = x1 - x0

    def X(v):
        return x0 + (min(v, SCALE_MAX) / SCALE_MAX) * span

    lbl_h = text_h(d, "x", f_small)
    row_h = int((26 if compact else 20) * s)
    gap = int((52 if compact else 48) * s)

    # reserve the bottom first: ticks, then caption
    tick_y = cap_y - int(30 * s)
    plot_bottom = tick_y - int(26 * s)
    plot_top = head_bottom + int(18 * s)

    # two rows, vertically centred in the available space
    block = row_h * 2 + gap
    clean_top = plot_top + max(0, (plot_bottom - plot_top - block) // 2)
    poison_top = clean_top + row_h + gap

    ov_lo = max(CLEAN_LO, min(v for _, v, _ in PAYLOADS))
    ov_hi = min(CLEAN_HI, max(v for _, v, _ in PAYLOADS))
    p_lo = min(v for _, v, _ in PAYLOADS)
    p_hi = max(v for _, v, _ in PAYLOADS)

    # overlap boundary lines, drawn behind everything so they read as guides
    for v in (ov_lo, ov_hi):
        x = X(v)
        y = clean_top - int(4 * s)
        while y < poison_top + row_h + int(4 * s):
            d.line([x, y, x, min(y + int(5 * s), poison_top + row_h + int(4 * s))],
                   fill=c["red"], width=max(1, int(s)))
            y += int(10 * s)
    # clean band
    d.rectangle([X(CLEAN_LO), clean_top, X(CLEAN_HI), clean_top + row_h], fill=c["band"])
    d.rectangle([X(CLEAN_LO), clean_top, X(CLEAN_HI), clean_top + row_h],
                outline=c["line"], width=max(1, int(s)))

    # poisoned band
    d.rectangle([X(p_lo), poison_top, X(p_hi), poison_top + row_h], fill=c["redband"])
    d.rectangle([X(p_lo), poison_top, X(p_hi), poison_top + row_h],
                outline=c["red"], width=max(1, int(s)))

    # row labels, above their bar, at the plot's left edge
    d.text((x0, clean_top - lbl_h - int(7 * s)), "clean corpus  20.4 – 84.7",
           font=f_small, fill=c["mute"])
    d.text((x0, poison_top - lbl_h - int(7 * s)), "poisoned payloads  77.2 – 115.8",
           font=f_small, fill=c["red"])

    # mean marker through the clean band
    mx = X(CLEAN_MEAN)
    d.line([mx, clean_top - int(3 * s), mx, clean_top + row_h + int(3 * s)],
           fill=c["dim"], width=max(1, int(s)))

    # payload positions marked on the poison band
    for name, val, highlight in PAYLOADS:
        px = X(val)
        d.line([px, poison_top - int(4 * s), px, poison_top + row_h + int(4 * s)],
               fill=c["red"] if highlight else c["dim"], width=max(1, int(s)))

    # baseline + ticks
    d.line([x0, tick_y, x1, tick_y], fill=c["line"], width=max(1, int(s)))
    for v in (0, 40, 80, 120):
        tx = X(v)
        d.line([tx, tick_y, tx, tick_y + int(4 * s)], fill=c["line"], width=max(1, int(s)))
        tw = d.textlength(str(v), font=f_small)
        d.text((min(tx - tw / 2, x1 - tw), tick_y + int(8 * s)),
               str(v), font=f_small, fill=c["dim"])

    # the overlap interval, labelled in the gap at the plot's left edge
    ov_lbl = f"overlap {ov_lo:.1f}–{ov_hi:.1f}"
    d.text((x0, clean_top + row_h + int(15 * s)), ov_lbl, font=f_small, fill=c["red"])

    return img


for theme in ("dark", "light"):
    # The post renders the hero in a 500px slot, so render at 2x for sharpness.
    hero = render(1068, 808, theme, 2.84, compact=True)
    hero.save(OUT / ("hero.png" if theme == "dark" else "hero-light.png"))
    card = render(1200, 630, theme, 2.2)
    card.save(OUT / ("card.png" if theme == "dark" else "card-light.png"))
    print(f"{theme}: hero 1068x808, card 1200x630")

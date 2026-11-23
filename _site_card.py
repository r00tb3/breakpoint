"""Render the site social card in both themes.

Same composition as the post cards: kicker pill, stacked display title, rule,
two-line subtitle on the left; one drawn object on the right; metadata and
brand along the footer. The object here is the BP monogram, since the site
has no single subject.

Run from the repo root:  python3 _site_card.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
ROOT = Path(__file__).parent
FDIR = ROOT / "fonts"
OUT = ROOT / "assets"

PALETTES = {
    "dark": dict(
        bg=(10, 10, 10), ink=(234, 234, 234), mute=(138, 138, 138),
        red=(230, 25, 25), line=(42, 42, 42), panel=(17, 17, 17),
        grid=(17, 17, 17), brand=(104, 101, 96),
    ),
    "light": dict(
        bg=(244, 244, 240), ink=(10, 10, 10), mute=(95, 95, 92),
        red=(196, 20, 20), line=(210, 208, 202), panel=(255, 255, 255),
        grid=(233, 232, 227), brand=(150, 148, 143),
    ),
}


def F(name, size):
    return ImageFont.truetype(str(FDIR / name), max(1, int(round(size))))


def fit(text, name, size, maxw, minsize=18):
    while size > minsize:
        f = F(name, size)
        if f.getlength(text) <= maxw:
            return f
        size -= 2
    return F(name, minsize)


def build(theme):
    c = PALETTES[theme]
    img = Image.new("RGB", (W, H), c["bg"])
    d = ImageDraw.Draw(img)

    for gx in range(0, W, 60):
        d.line([(gx, 0), (gx, H)], fill=c["grid"])
    for gy in range(0, H, 60):
        d.line([(0, gy), (W, gy)], fill=c["grid"])
    d.rectangle([0, 0, 6, H], fill=c["red"])

    # ── kicker pill ──
    kick_f = F("JetBrainsMono-Regular.ttf", 14)
    kicker = "SYSTEMS SECURITY"
    kw = kick_f.getlength(kicker)
    d.rectangle([92, 66, 92 + kw + 28, 96], outline=c["red"], width=1)
    d.text((106, 74), kicker, font=kick_f, fill=c["red"])

    # ── display title ──
    small_f = F("ArchivoBlack-Regular.ttf", 40)
    t_f = fit("BASEBAND", "ArchivoBlack-Regular.ttf", 78, 452)
    s_f = fit("UP.", "ArchivoBlack-Regular.ttf", 78, 452)
    d.text((94, 128), "FROM", font=small_f, fill=c["mute"])
    d.text((92, 176), "BASEBAND", font=t_f, fill=c["ink"])
    d.text((92, 176 + t_f.size + 6), "UP.", font=s_f, fill=c["red"])

    # ── rule + subtitle ──
    y = 176 + t_f.size + 6 + s_f.size + 34
    d.line([(92, y), (556, y)], fill=c["line"])
    sub_f = F("JetBrainsMono-Regular.ttf", 18)
    d.text((92, y + 18), "Modem firmware, telecom", font=sub_f, fill=c["mute"])
    d.text((92, y + 44), "networks, ML security.", font=sub_f, fill=c["mute"])

    # ── monogram ──
    BX0, BY0, BW = 706, 124, 352
    BH = BW
    d.rectangle([BX0, BY0, BX0 + BW, BY0 + BH], fill=c["panel"],
                outline=c["ink"], width=2)
    d.rectangle([BX0 + 12, BY0 + 12, BX0 + 24, BY0 + 24], fill=c["red"])

    bp_f = F("ArchivoBlack-Regular.ttf", 150)
    label = "BP"
    tw = bp_f.getlength(label)
    b = d.textbbox((0, 0), label, font=bp_f)
    d.text((BX0 + (BW - tw) / 2, BY0 + (BH - (b[3] - b[1])) / 2 - 34),
           label, font=bp_f, fill=c["ink"])

    dom_f = F("JetBrainsMono-Regular.ttf", 16)
    dom = "BREAKPOINT.CX"
    dw = dom_f.getlength(dom)
    d.text((BX0 + (BW - dw) / 2, BY0 + BH - 62), dom, font=dom_f, fill=c["mute"])

    # ── footer ──
    meta_f = F("JetBrainsMono-Regular.ttf", 13)
    d.text((92, 566), "BASEBAND   ·   TELCO   ·   AI SECURITY",
           font=meta_f, fill=c["mute"])
    brand_f = F("ArchivoBlack-Regular.ttf", 15)
    brand = "BREAKPOINT"
    d.text((1108 - brand_f.getlength(brand), 564), brand,
           font=brand_f, fill=c["brand"])

    path = OUT / ("site-card.png" if theme == "dark" else "site-card-light.png")
    img.save(path, "PNG", optimize=True)
    print("wrote", path, path.stat().st_size, "bytes")


for th in ("dark", "light"):
    build(th)

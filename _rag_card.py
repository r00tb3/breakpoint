"""Render the RAG social card and hero in both themes.

Same composition as the baseband card: kicker pill, stacked display title,
rule, two-line subtitle on the left; a single drawn object on the right;
metadata and brand along the footer. The object here is ten documents, nine
of them struck out — the article's headline measurement.

Run from the repo root:  python3 _rag_card.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
ROOT = Path(__file__).parent
FDIR = ROOT / "fonts"
OUT = ROOT / "rag-poisoning"

# artwork-only crop for the in-article hero; 1.33 ratio, centred on the
# document grid (which spans x 648-1140, y 240-500) with even margin.
CROP = (630, 174, 1150, 566)

PALETTES = {
    "dark": dict(
        bg=(10, 10, 10), ink=(234, 234, 234), mute=(138, 138, 138),
        dim=(90, 90, 90), red=(230, 25, 25), line=(42, 42, 42),
        panel=(17, 17, 17), grid=(17, 17, 17), brand=(104, 101, 96),
        label=(196, 196, 192), docfill=(26, 26, 26), docline=(58, 58, 58),
        textline=(72, 72, 72),
    ),
    "light": dict(
        bg=(244, 244, 240), ink=(10, 10, 10), mute=(95, 95, 92),
        dim=(140, 140, 136), red=(196, 20, 20), line=(210, 208, 202),
        panel=(255, 255, 255), grid=(233, 232, 227), brand=(150, 148, 143),
        label=(52, 52, 50), docfill=(252, 252, 250), docline=(206, 204, 198),
        textline=(196, 194, 188),
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


def doc_card(d, x, y, w, h, c, struck, index):
    """One document: a card with text rules, struck out if it was rejected."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=4,
                        fill=c["docfill"], outline=c["docline"], width=2)
    # faux text lines
    lines = (0.62, 0.86, 0.74, 0.45)
    for i, frac in enumerate(lines):
        ly = y + 11 + i * 8
        d.rectangle([x + 9, ly, x + 9 + int((w - 18) * frac), ly + 3],
                    fill=c["textline"])
    if struck:
        d.line([x + 7, y + h - 7, x + w - 7, y + 7], fill=c["red"], width=3)
    else:
        # the survivor gets a marker so the eye lands on it
        d.rectangle([x + 1, y + 1, x + w - 1, y + h - 1],
                    outline=c["ink"], width=2)


def build(theme):
    c = PALETTES[theme]
    img = Image.new("RGB", (W, H), c["bg"])
    d = ImageDraw.Draw(img)

    # background grid, matching the baseband card
    for gx in range(0, W, 60):
        d.line([(gx, 0), (gx, H)], fill=c["grid"])
    for gy in range(0, H, 60):
        d.line([(0, gy), (W, gy)], fill=c["grid"])
    d.rectangle([0, 0, 6, H], fill=c["red"])

    # ── kicker pill ──
    kick_f = F("JetBrainsMono-Regular.ttf", 14)
    kicker = "AI SECURITY"
    kw = kick_f.getlength(kicker)
    d.rectangle([92, 66, 92 + kw + 28, 96], outline=c["red"], width=1)
    d.text((106, 74), kicker, font=kick_f, fill=c["red"])

    # ── display title, same three-line treatment as the baseband card ──
    small_f = F("ArchivoBlack-Regular.ttf", 40)
    t_f = fit("NINE", "ArchivoBlack-Regular.ttf", 78, 452)
    s_f = fit("OF TEN", "ArchivoBlack-Regular.ttf", 78, 452)
    d.text((94, 128), "THE", font=small_f, fill=c["mute"])
    d.text((92, 176), "NINE", font=t_f, fill=c["ink"])
    d.text((92, 176 + t_f.size + 6), "OF TEN", font=s_f, fill=c["red"])

    # ── rule + subtitle ──
    y = 176 + t_f.size + 6 + s_f.size + 34
    d.line([(92, y), (556, y)], fill=c["line"])
    sub_f = F("JetBrainsMono-Regular.ttf", 18)
    d.text((92, y + 18), "Measuring three defences in a", font=sub_f, fill=c["mute"])
    d.text((92, y + 44), "RAG poisoning lab", font=sub_f, fill=c["mute"])

    # ── artwork: ten documents, nine struck out, resting on a ground line ──
    GROUND = 500
    d.line([(600, GROUND), (1150, GROUND)], fill=c["line"], width=2)

    AW_X0 = 648
    CW, CH, GX, GY = 84, 100, 18, 14
    grid_h = 2 * CH + GY
    AW_Y0 = GROUND - grid_h

    # caption above the grid, the way the baseband card labels its arrows
    cap_f = F("JetBrainsMono-Regular.ttf", 13)
    d.text((AW_X0, AW_Y0 - 46), "9 of 10 clean documents rejected",
           font=cap_f, fill=c["red"])
    d.text((AW_X0, AW_Y0 - 26), "by the lab's own keyword filter",
           font=cap_f, fill=c["mute"])

    for i in range(10):
        col, row = i % 5, i // 5
        x = AW_X0 + col * (CW + GX)
        yy = AW_Y0 + row * (CH + GY)
        doc_card(d, x, yy, CW, CH, c, struck=(i != 9), index=i)

    # ── footer ──
    meta_f = F("JetBrainsMono-Regular.ttf", 13)
    d.text((92, 566), "RAG-POISONING-LAB   ·   GPT-2   ·   NOMIC-EMBED-TEXT",
           font=meta_f, fill=c["mute"])
    brand_f = F("ArchivoBlack-Regular.ttf", 15)
    brand = "BREAKPOINT"
    d.text((1108 - brand_f.getlength(brand), 564), brand,
           font=brand_f, fill=c["brand"])

    path = OUT / ("card.png" if theme == "dark" else "card-light.png")
    img.save(path, "PNG", optimize=True)
    print("wrote", path, path.stat().st_size, "bytes")

    hero_path = OUT / ("hero.png" if theme == "dark" else "hero-light.png")
    img.crop(CROP).save(hero_path, "PNG", optimize=True)
    print("wrote", hero_path, hero_path.stat().st_size, "bytes")


for th in ("dark", "light"):
    build(th)

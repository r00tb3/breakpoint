"""Render the social card in both themes.

Original composition: title block, phone on the ground, exchange arrows, base
station. Each arrow now carries its SIP message above it.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

W, H = 1200, 630
# phone + arrows + tower, without the title block
CROP = (606, 112, 1140, 516)
FDIR = "/mnt/f/ai/Projects/blog/fonts"
OUTDIR = "/mnt/f/ai/Projects/blog/cve-2023-24033"

PALETTES = {
    "dark": dict(
        bg=(10, 10, 10), ink=(234, 234, 234), mute=(138, 138, 138),
        dim=(90, 90, 90), red=(230, 25, 25), line=(42, 42, 42),
        panel=(17, 17, 17), grid=(17, 17, 17), brand=(104, 101, 96),
        arrow=(104, 104, 100), label=(196, 196, 192),
    ),
    "light": dict(
        bg=(244, 244, 240), ink=(10, 10, 10), mute=(95, 95, 92),
        dim=(140, 140, 136), red=(196, 20, 20), line=(210, 208, 202),
        panel=(255, 255, 255), grid=(233, 232, 227), brand=(150, 148, 143),
        arrow=(150, 148, 142), label=(52, 52, 50),
    ),
}


def pick(cands):
    for p in cands:
        if os.path.exists(p):
            return p
    return None


DISPLAY = pick([f"{FDIR}/ArchivoBlack-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"])
MONO = pick([f"{FDIR}/JetBrainsMono-Regular.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"])
MONO_B = pick([f"{FDIR}/JetBrainsMono-Bold.ttf", MONO])

if not DISPLAY:
    raise SystemExit("no display font available")


def F(path, size):
    return ImageFont.truetype(path, size)


def fit(text, path, size, maxw, minsize=16):
    while size > minsize:
        f = F(path, size)
        if f.getlength(text) <= maxw:
            return f
        size -= 2
    return F(path, minsize)


def arrow(d, x0, x1, y, col, w=2, head=12):
    d.line([(x0, y), (x1, y)], fill=col, width=w)
    s = 1 if x1 > x0 else -1
    d.polygon([(x1, y), (x1 - head * s, y - 7), (x1 - head * s, y + 7)], fill=col)


def burst(d, cx, cy, outer, inner, col):
    pts = []
    for i in range(16):
        r = outer if i % 2 == 0 else inner
        a = math.pi * i / 8
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=col)


def build(theme):
    c = PALETTES[theme]
    img = Image.new("RGB", (W, H), c["bg"])
    d = ImageDraw.Draw(img)

    for gx in range(0, W, 60):
        d.line([(gx, 0), (gx, H)], fill=c["grid"])
    for gy in range(0, H, 60):
        d.line([(0, gy), (W, gy)], fill=c["grid"])
    d.rectangle([0, 0, 6, H], fill=c["red"])

    # ── text block ────────────────────────────────────────────────
    kicker_f = F(MONO, 14)
    kicker = "VULNERABILITY RESEARCH"
    kw = kicker_f.getlength(kicker)
    d.rectangle([92, 66, 92 + kw + 28, 96], outline=c["red"], width=1)
    d.text((106, 74), kicker, font=kicker_f, fill=c["red"])

    small_f = F(DISPLAY, 40)
    t_f = fit("ELEVENTH", DISPLAY, 74, 452)
    s_f = fit("SLOT", DISPLAY, 74, 452)
    d.text((94, 128), "THE", font=small_f, fill=c["mute"])
    d.text((92, 176), "ELEVENTH", font=t_f, fill=c["ink"])
    d.text((92, 176 + t_f.size + 6), "SLOT", font=s_f, fill=c["red"])

    y = 176 + t_f.size + 6 + s_f.size + 34
    d.line([(92, y), (556, y)], fill=c["line"])
    sub_f = F(MONO, 18)
    d.text((92, y + 18), "An IMS SDP heap overflow in", font=sub_f, fill=c["mute"])
    d.text((92, y + 44), "Exynos modem firmware", font=sub_f, fill=c["mute"])

    # ── phone ────────────────────────────────────────────────────
    GROUND = 500
    d.line([(600, GROUND), (1140, GROUND)], fill=c["line"], width=2)

    d.rounded_rectangle([636, 190, 754, GROUND], radius=18, fill=c["panel"],
                        outline=c["ink"], width=2)
    d.rounded_rectangle([648, 214, 742, GROUND - 22], radius=6,
                        fill=c["bg"], outline=c["line"])
    d.line([(676, 202), (714, 202)], fill=c["ink"], width=3)
    d.line([(680, 486), (710, 486)], fill=c["dim"], width=3)
    for i, wd in enumerate((54, 44, 62, 34)):
        yy = 250 + i * 18
        d.rectangle([660, yy, 660 + wd, yy + 5], fill=c["dim"])
    d.rectangle([660, 340, 706, 346], fill=c["red"])

    # ── exchange arrows with their messages ──────────────────────
    AX0, AX1 = 772, 972
    ys = [252, 306, 360, 414, 468]
    steps = [
        (1, "REGISTER", False),
        (-1, "401 Unauthorized", False),
        (1, "REGISTER · credentials", False),
        (-1, "200 OK", False),
        (-1, "INVITE · a=accept-types ×11", True),
    ]
    lbl_f = F(MONO, 13)

    for (dirn, label, fatal), yy in zip(steps, ys):
        d.text(((AX0 + AX1) / 2 - lbl_f.getlength(label) / 2, yy - 29), label,
               font=lbl_f, fill=c["red"] if fatal else c["label"])
        if fatal:
            arrow(d, AX1, AX0, yy, c["red"], w=3, head=14)
        else:
            arrow(d, AX0 if dirn > 0 else AX1, AX1 if dirn > 0 else AX0,
                  yy, c["arrow"], w=2, head=11)

    burst(d, 760, 469, 13, 5, c["red"])

    # ── base station ─────────────────────────────────────────────
    BX, TOPY, GB = 1056, 230, GROUND
    HT, HB = 15, 45

    def half(yy):
        return HT + (yy - TOPY) / (GB - TOPY) * (HB - HT)

    d.line([(BX - HB, GB), (BX - HT, TOPY)], fill=c["ink"], width=3)
    d.line([(BX + HB, GB), (BX + HT, TOPY)], fill=c["ink"], width=3)

    levels = [GB, 455, 405, 355, 305, 265, TOPY]
    for i, yy in enumerate(levels):
        hw = half(yy)
        d.line([(BX - hw, yy), (BX + hw, yy)], fill=c["ink"], width=2)
        if i + 1 < len(levels):
            y2 = levels[i + 1]
            hw2 = half(y2)
            d.line([(BX - hw, yy), (BX + hw2, y2)], fill=c["ink"], width=1)
            d.line([(BX + hw, yy), (BX - hw2, y2)], fill=c["ink"], width=1)

    d.rectangle([BX - 24, TOPY - 4, BX + 24, TOPY + 3], fill=c["ink"])
    for px in (BX - 23, BX - 7, BX + 9):
        d.rectangle([px, 172, px + 12, TOPY - 4], fill=c["panel"], outline=c["ink"], width=2)
        d.rectangle([px + 2, 178, px + 10, 183], fill=c["red"])

    for rad in (48, 72, 96):
        d.arc([BX - rad, 214 - rad, BX + rad, 214 + rad], start=150, end=210,
              fill=c["red"], width=2)

    # ── footer ───────────────────────────────────────────────────
    meta_f = F(MONO, 13)
    d.text((92, 566), "CVE-2023-24033   ·   SHANNON S5123   ·   ARM32 / THUMB",
           font=meta_f, fill=c["mute"])
    brand_f = F(DISPLAY, 15)
    brand = "BREAKPOINT"
    d.text((1108 - brand_f.getlength(brand), 564), brand, font=brand_f, fill=c["brand"])

    path = f"{OUTDIR}/card.png" if theme == "dark" else f"{OUTDIR}/card-light.png"
    img.save(path, "PNG", optimize=True)
    print("wrote", path, os.path.getsize(path), "bytes")

    # the artwork alone, for the article hero
    hero_path = f"{OUTDIR}/hero.png" if theme == "dark" else f"{OUTDIR}/hero-light.png"
    img.crop(CROP).save(hero_path, "PNG", optimize=True)
    print("wrote", hero_path, os.path.getsize(hero_path), "bytes")


for th in ("dark", "light"):
    build(th)

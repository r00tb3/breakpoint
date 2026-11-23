"""Inject canonical + og:url + absolute og:image into the static pages.

Run from the repo root:  python3 _seo.py
Idempotent: safe to run repeatedly.
"""
import re
from pathlib import Path

BASE = "https://breakpoint.cx"
ROOT = Path(__file__).parent

PAGES = {
    "index.html": f"{BASE}/",
    "rag-poisoning/index.html": f"{BASE}/rag-poisoning/",
    "cve-2023-24033/index.html": f"{BASE}/cve-2023-24033/",
    "about/index.html": f"{BASE}/about/",
}

IMAGE = {
    "index.html": f"{BASE}/assets/site-card.png",
    "rag-poisoning/index.html": f"{BASE}/rag-poisoning/card.png",
    "cve-2023-24033/index.html": f"{BASE}/cve-2023-24033/card.png",
    "about/index.html": f"{BASE}/assets/site-card.png",
}

IMAGE_ALT = {
    "index.html": "Breakpoint — the BP monogram on a black grid",
    "rag-poisoning/index.html": "Ten document cards, nine struck through in red, captioned nine of ten clean documents rejected",
    "cve-2023-24033/index.html": "SIP call flow from REGISTER to an INVITE whose SDP list overflows the modem parser",
    "about/index.html": "Breakpoint — the BP monogram on a black grid",
}


def strip_existing(html: str) -> str:
    """Remove any canonical/og:url/og:image tags so the script is idempotent."""
    html = re.sub(r'\n?<link rel="canonical"[^>]*>', "", html)
    html = re.sub(r'\n?<meta property="og:url"[^>]*>', "", html)
    html = re.sub(r'\n?<meta property="og:image(?::[a-z]+)?"[^>]*>', "", html)
    html = re.sub(r'\n?<meta name="twitter:(?:card|image)"[^>]*>', "", html)
    return html


def inject(html: str, url: str, image: str | None, alt: str | None = None) -> str:
    tags = [f'<link rel="canonical" href="{url}">',
            f'<meta property="og:url" content="{url}">']
    if image:
        tags += [
            f'<meta property="og:image" content="{image}">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
        ]
        if alt:
            tags.append(f'<meta property="og:image:alt" content="{alt}">')
        tags += [
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:image" content="{image}">',
        ]
    block = "\n".join(tags)
    # place immediately before </head> so ordering never matters
    return html.replace("</head>", block + "\n</head>", 1)


for rel, url in PAGES.items():
    p = ROOT / rel
    if not p.exists():
        print(f"skip (missing): {rel}")
        continue
    html = p.read_text(encoding="utf-8")
    html = strip_existing(html)
    html = inject(html, url, IMAGE[rel], IMAGE_ALT[rel])
    p.write_text(html, encoding="utf-8")
    print(f"updated: {rel}")

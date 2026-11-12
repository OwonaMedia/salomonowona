#!/usr/bin/env python3
"""Generate static SEO shop pages for salomonowona.com from shop/products.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOP = ROOT / "shop"
CAT = json.loads((SHOP / "products.json").read_text(encoding="utf-8"))
PRODUCTS = CAT["products"]
CATEGORIES = CAT["categories"]
BASE = "https://salomonowona.com"
AUTHOR = "Salomon Owona"

def esc(s) -> str:
    return (
        str(s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

def euro(cents) -> str:
    if cents is None:
        return ""
    return f"{cents/100:.2f}".replace(".", ",") + " €"

LANG_LABELS = {"de": "Deutsch", "en": "Englisch", "fr": "Französisch", "es": "Spanisch", "pt": "Portugiesisch", "sw": "Swahili"}


def book_lang(p) -> str:
    return str(p.get("language") or "de").lower()[:2]


def lang_label(p) -> str:
    code = book_lang(p)
    return LANG_LABELS.get(code, code)


def cat_by_id(cid):
    return next(c for c in CATEGORIES if c["id"] == cid)

def products_in(cid):
    return [p for p in PRODUCTS if p.get("category") == cid and p.get("type") != "collection"]

def product(slug):
    return next(p for p in PRODUCTS if p["slug"] == slug)

GOAT = (
    '<script>window.goatcounter={path:function(){return "/"+location.hostname.replace("www.","")+location.pathname}}</script>'
    '<script data-goatcounter="https://stats.owona.de/count" async src="https://stats.owona.de/count.js"></script>'
)

SHOP_JSON = json.dumps(
    {
        "shopId": CAT["shopId"],
        "shopLive": CAT["shopLive"],
        "apiBase": CAT["apiBase"],
        "xafRate": CAT["xafRate"],
        "products": [
            {
                "id": p["id"],
                "slug": p["slug"],
                "title": p["title"],
                "priceCents": p.get("priceCents"),
                "fulfillment": p["fulfillment"],
                "sellable": p.get("sellable"),
                "language": p.get("language") or "de",
            }
            for p in PRODUCTS
        ],
    },
    ensure_ascii=False,
    separators=(",", ":"),
)


def site_chrome_assets():
    """Reuse the exact Tailwind include and #page-style from de.html."""
    de = (ROOT / "de.html").read_text(encoding="utf-8")
    tw = re.search(
        r'<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4\.3\.3"[^>]*></script>',
        de,
    )
    style = re.search(r'<style id="page-style">[\s\S]*?</style>', de)
    if not tw or not style:
        raise RuntimeError("de.html is missing Tailwind or #page-style — shop must reuse them")
    return tw.group(0) + "\n    " + style.group(0)


def head(title, desc, canonical, *, og_type="website", image=None, schema=None, extra=""):
    img = image or f"{BASE}/Salomon.webp"
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(desc)}">
    <link rel="canonical" href="{esc(canonical)}">
    <meta name="robots" content="index,follow">
    <meta property="og:type" content="{esc(og_type)}">
    <meta property="og:site_name" content="Salomon Owona">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(desc)}">
    <meta property="og:url" content="{esc(canonical)}">
    <meta property="og:image" content="{esc(img)}">
    <meta property="og:locale" content="de_DE">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(title)}">
    <meta name="twitter:description" content="{esc(desc)}">
    <meta name="author" content="{AUTHOR}">
    <link rel="describedby" href="{BASE}/llms.txt">
    {site_chrome_assets()}
    <link rel="stylesheet" href="/shop/shop.css">
    <script>window.SO_SHOP={SHOP_JSON};</script>
    {schema or ""}
    {extra}
</head>
"""


def header(current="shop"):
    def cur(name):
        return ' aria-current="page"' if current == name else ""

    # Exact same header, sidebar, language switcher and radio as de.html.
    # Section links point at /de#… so the shop stays inside the same site.
    return f"""<body>
<div id="site-root">
    <header>
        <div class="nav-inner">
            <a href="/de#home" class="logo">Salomon Owona</a>

            <div class="audio-controls">
                <button type="button" class="play-btn" onclick="toggleArchiveRadio()" id="playIcon" aria-label="Salomon Radio abspielen" aria-pressed="false" data-label-play="Salomon Radio abspielen" data-label-pause="Salomon Radio pausieren">▶</button>
                <div class="track-info" id="trackName">Salomon Radio</div>
            </div>
            <button type="button" class="hamburger" id="navToggle" aria-label="Menü öffnen" aria-expanded="false" aria-controls="sidebar" data-label-open="Menü öffnen" data-label-close="Menü schließen">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </header>
    <div class="overlay" id="overlay"></div>
    <div class="sidebar" id="sidebar">
        <nav class="sidebar-nav">
            <a href="/de#home">Home</a>
            <a href="/de#about">Über mich</a>
            <a href="/de#doing">Was ich tue</a>
            <a href="/de#values">Werte</a>
            <a href="/de#projects">Projekte</a>
            <a href="/de#buecher">Bücher</a>
            <a href="/de#contact">Kontakt</a>
            <a href="/shop/"{cur("shop")}>Shop</a>
            <a href="/shop/warenkorb"{cur("cart")}>Warenkorb (<span data-cart-count>0</span>)</a>
            <div class="lang-switcher">
                <button type="button" class="lang-btn" onclick="switchLanguage('sw')" aria-label="SW">SW</button>
                <button type="button" class="lang-btn active" onclick="switchLanguage('de')" aria-label="DE" aria-current="true">DE</button>
                <button type="button" class="lang-btn" onclick="switchLanguage('en')" aria-label="EN">EN</button>
                <button type="button" class="lang-btn" onclick="switchLanguage('fr')" aria-label="FR">FR</button>
            </div>
        </nav>
    </div>
    <main>
"""


def footer():
    # Exact de.html footer (Patreon, social, legal), plus AGB/Widerruf for the shop,
    # then the same radio player, radio-persist.js and GoatCounter.
    return f"""    </main>
    <footer>
        <div class="container-shifted">
            <div style="display: flex; flex-direction: column; gap: 2rem; align-items: center;">
                <!-- Patreon Widget -->
                <div class="patreon-widget">
                    <iframe src="https://patreon.com/SalomonO" frameborder="0" width="100%" height="200" style="border-radius: 8px;"></iframe>
                </div>

                <!-- Social Media Icons -->
                <div class="social-icons">
                    <a href="https://www.tiktok.com/@salomon.rocks" class="social-icon tiktok" target="_blank" rel="noopener noreferrer" title="TikTok">
                        <span class="social-text">📱</span>
                    </a>
                    <a href="https://www.facebook.com/share/19bWcdUGQK/" class="social-icon facebook" target="_blank" rel="noopener noreferrer" title="Facebook">
                        <span class="social-text">📘</span>
                    </a>
                    <a href="https://www.instagram.com/salomon.rocks/" class="social-icon instagram" target="_blank" rel="noopener noreferrer" title="Instagram">
                        <span class="social-text">📷</span>
                    </a>
                    <a href="https://www.youtube.com/@salomonowona" class="social-icon youtube" target="_blank" rel="noopener noreferrer" title="YouTube">
                        <span class="social-text">📺</span>
                    </a>
                    <a href="https://www.amazon.de/s?i=stripbooks&rh=p_27%3ASalomon%2BOwona&s=relevancerank&text=Salomon+Owona&ref=dp_byline_sr_book_1" class="social-icon amazon" target="_blank" rel="noopener noreferrer" title="E-Books">
                        <span class="social-text">📦</span>
                    </a>
                </div>

                <nav class="legal-links" aria-label="Rechtliches" style="display:flex;flex-wrap:wrap;gap:1rem;justify-content:center;margin-bottom:1rem;font-size:0.9rem;">
                    <a href="/shop/" style="color:var(--accent);">Shop</a>
                    <a href="/impressum" style="color:var(--accent);">Impressum</a>
                    <a href="/datenschutz" style="color:var(--accent);">Datenschutz</a>
                    <a href="/shop/agb" style="color:var(--accent);">AGB</a>
                    <a href="/shop/widerruf" style="color:var(--accent);">Widerruf</a>
                </nav>
                <p>&copy; 1981-2026 Salomon Firmin Owona. Zwischen Welten.</p>
            </div>
        </div>
    </footer>
</div>
    <audio id="liveRadioPlayer" preload="none" playsinline style="display: none;"></audio>
    <script src="/radio-persist.js" defer></script>
    <script src="/shop/shop.js" defer></script>
{GOAT}
</body>
</html>
"""


def test_banner():
    if is_live():
        return ""
    return """<div class="values-box shop-draft" role="status">
                    <p class="values-lead">Testmodus.</p>
                    <p>Der Shop ist angelegt, verkauft aber noch nicht. Es wird nichts berechnet, und es geht keine Bestellung hinaus. Der Verkauf startet erst, wenn Salomon Owona den Shop ausdrücklich freigibt.</p>
                </div>"""


def chips(active=None):
    bits = []
    ac = ' aria-current="page"' if not active else ""
    bits.append('<a href="/shop/"' + ac + ">Alle</a>")
    for c in CATEGORIES:
        is_a = active == c["id"]
        ac = ' aria-current="page"' if is_a else ""
        bits.append(
            '<a href="/shop/kategorie/' + c["id"] + '"' + ac + ">" + esc(c["short"]) + "</a>"
        )
    return '<nav class="shop-cats" aria-label="Kategorien">' + "".join(bits) + "</nav>"


def cover_html(p, lg=False, cls="shop-cover"):
    title = esc(p["title"])
    img_cls = "shop-cover-lg" if lg else "shop-cover"
    if p.get("cover"):
        src = p["coverLg"] if lg and p.get("coverLg") else p["cover"]
        jpg = p.get("coverLgJpg") if lg and p.get("coverLgJpg") else p.get("coverJpg")
        style = (
            "width:220px;max-width:100%;height:auto;display:block;margin-bottom:1.5rem;"
            "border-radius:4px;border:1px solid var(--border);"
            if lg else
            "width:120px;height:auto;display:block;margin-bottom:1.25rem;"
            "border-radius:4px;border:1px solid var(--border);"
        )
        return (
            f'<picture>\n'
            f'                        <source type="image/webp" srcset="{esc(src)}">\n'
            f'                        <img class="{img_cls}" src="{esc(jpg or src)}" alt="Cover: {title}" width="400" height="640" style="{style}">\n'
            f'                    </picture>'
        )
    return '<span class="project-icon" aria-hidden="true">📖</span>'


def is_live():
    return bool(CAT.get("shopLive"))


def badge(p):
    if p.get("badge"):
        return f'<span class="shop-muted">{esc(p["badge"])}</span>'
    return ""


def card(p):
    price = (
        f'<span class="shop-price" style="color:var(--accent);font-weight:600">{euro(p["priceCents"])}</span>'
        if p.get("priceCents")
        else '<span class="shop-muted" style="color:var(--text-muted)">Bei Amazon</span>'
    )
    words = (
        f' · ca. {p["wordCount"]:,} Wörter'.replace(",", ".")
        if p.get("wordCount")
        else ""
    )
    cat = cat_by_id(p["category"])["short"]
    blurb = (p.get("blurb") or "")[:160]
    if p.get("blurb") and len(p["blurb"]) > 160:
        blurb = blurb.rsplit(" ", 1)[0] + "…"
    desc = esc(blurb) if blurb else esc(cat)
    return (
        f'<div class="project-card">\n'
        f'                        {cover_html(p)}\n'
        f'                        <div class="project-title">{esc(p["title"])}</div>\n'
        f'                        <div class="project-desc">{desc}<br>{price}{words}<br>\n'
        f'                        <a href="/shop/{esc(p["slug"])}" style="color: var(--accent);">Zum Buch →</a></div>\n'
        f'                    </div>'
    )


def section(inner, sid=""):
    id_attr = f' id="{sid}"' if sid else ""
    return (
        f'        <section{id_attr}>\n'
        f'            <div class="container-shifted">\n'
        f'                {inner}\n'
        f'            </div>\n'
        f'        </section>\n'
    )


def schema_product(p):
    if p.get("type") == "collection":
        return ""
    url = f"{BASE}/shop/{p['slug']}"
    img = f"{BASE}{p['coverLg']}" if p.get("coverLg") else f"{BASE}/Salomon.webp"
    if is_live() and p.get("sellable"):
        avail = "https://schema.org/InStock"
    else:
        avail = "https://schema.org/PreOrder"
    offer = None
    if p.get("fulfillment") == "amazon" and p.get("amazonUrl"):
        offer = {
            "@type": "Offer",
            "url": p["amazonUrl"],
            "availability": "https://schema.org/InStock",
            "seller": {"@type": "Organization", "name": "Amazon"},
        }
    elif p.get("priceCents") is not None:
        offer = {
            "@type": "Offer",
            "url": url,
            "priceCurrency": "EUR",
            "price": f"{p['priceCents']/100:.2f}",
            "availability": avail,
            "seller": {"@type": "Person", "name": AUTHOR, "@id": f"{BASE}/#person"},
        }
    book = {
        "@type": "Book",
        "@id": url + "#book",
        "name": p["title"],
        "author": {"@type": "Person", "name": AUTHOR, "@id": f"{BASE}/#person"},
        "inLanguage": book_lang(p),
        "bookFormat": "https://schema.org/EBook",
        "image": img,
        "description": p.get("blurb") or "",
        "url": url,
        "creativeWorkStatus": "Published" if p.get("lektorat") or p.get("fulfillment") == "amazon" else "Draft",
        "additionalProperty": {"@type": "PropertyValue", "name": "KI-Hinweis", "value": "Mit Hilfe von KI erstellt"},
    }
    if p.get("wordCount"):
        book["wordCount"] = p["wordCount"]
    if p.get("amazonAsin"):
        book["isbn"] = p["amazonAsin"]
        book["sameAs"] = p["amazonUrl"]
    product = {
        "@type": "Product",
        "@id": url + "#product",
        "name": p["title"],
        "image": img,
        "description": p.get("blurb") or "",
        "brand": {"@type": "Brand", "name": AUTHOR},
        "author": {"@type": "Person", "name": AUTHOR, "@id": f"{BASE}/#person"},
        "category": cat_by_id(p["category"])["name"],
        "url": url,
    }
    if offer:
        product["offers"] = offer
    data = {"@context": "https://schema.org", "@graph": [book, product]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"



# ---------- pages ----------

def page_index():
    tiles = []
    for c in CATEGORIES:
        n = len(products_in(c["id"]))
        label = f"{n} Titel" if n else "Weitere Titel in Vorbereitung"
        tiles.append(
            '<div class="project-card">\n'
            '                        <div class="project-title">' + esc(c["name"]) + '</div>\n'
            '                        <div class="project-desc">' + esc(c["desc"]) + '<br>\n'
            '                        <span class="shop-muted">' + esc(label) + '</span><br>\n'
            '                        <a href="/shop/kategorie/' + c["id"] + '" style="color: var(--accent);">Zur Kategorie →</a></div>\n'
            '                    </div>'
        )
    own = [p for p in PRODUCTS if p["fulfillment"] == "own"]
    cards = "\n                    ".join(card(p) for p in own)
    amazon = [p for p in PRODUCTS if p["fulfillment"] == "amazon" and p.get("type") != "collection"]
    acards = "\n                    ".join(card(p) for p in amazon)
    desc = "E-Books von Salomon Owona: Herkunft, Musik, Liebe, E-Commerce, Krypto, Vibe Coding, Geschichte und Afro-Mythologie. Zahlung per Karte (EUR) oder Mobile Money (XAF) – Verkauf startet nach Freigabe."
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Shop | Salomon Owona",
        "url": f"{BASE}/shop/",
        "isPartOf": {"@type": "WebSite", "name": "Salomon Owona", "url": BASE + "/"},
        "about": {"@type": "Person", "@id": f"{BASE}/#person", "name": AUTHOR},
        "description": desc,
        "inLanguage": "de",
    }
    html = (
        head(
            "Shop | Salomon Owona",
            desc,
            f"{BASE}/shop/",
            schema='<script type="application/ld+json">'
            + json.dumps(schema, ensure_ascii=False)
            + "</script>",
        )
        + header("shop")
        + section(
            test_banner()
            + '\n                <p class="shop-crumbs"><a href="/de">Start</a> · Shop</p>\n'
            + "                <h1>Shop</h1>\n"
            + '                <p class="bio-text">E-Books von '
            + AUTHOR
            + ". Nur Deutsch, nur wo eine geprüfte Datei vorliegt. Digitale Lieferungen per E-Mail, Zahlung wie im Shop von Owona Media: Karte über Stripe in Euro oder MTN/Orange Money über NotchPay in CFA-Franc.</p>\n"
            + '                <p class="shop-ai">Alle eigenen Titel: Mit Hilfe von KI erstellt.</p>\n'
            + "                "
            + chips()
        )
        + section(
            "                <h2>Kategorien</h2>\n"
            '                <div class="project-grid">\n                    '
            + "\n                    ".join(tiles)
            + "\n                </div>"
        )
        + section(
            "                <h2>Eigene Titel</h2>\n"
            '                <div class="project-grid">\n                    '
            + cards
            + "\n                </div>"
        )
        + section(
            "                <h2>Afro-Mythologie bei Amazon</h2>\n"
            '                <p class="shop-muted">Diese Titel haben keine eigene Shop-Datei; der Kauf erfolgt über Amazon.</p>\n'
            '                <div class="project-grid">\n                    '
            + acards
            + "\n                </div>"
        )
        + footer()
    )
    (SHOP / "index.html").write_text(html, encoding="utf-8")


def page_category(c):
    items = products_in(c["id"])
    if items:
        body = (
            '<div class="project-grid">\n                    '
            + "\n                    ".join(card(p) for p in items)
            + "\n                </div>"
        )
    else:
        body = (
            '<div class="values-box">\n'
            "                    <p>In <strong>"
            + esc(c["name"])
            + "</strong> sind noch keine eigenen Titel im Katalog. "
            "Weitere Bücher sind in Vorbereitung und erscheinen hier, sobald eine lektorierte deutsche Fassung vorliegt.</p>\n"
            "                </div>"
        )
    extra = ""
    if c["id"] == "afro-mythologie":
        extra = (
            '<p class="shop-muted" style="margin-top:1.5rem">Vier Mythologie-Titel sind über Amazon erhältlich: '
            "Horus, Ra, Eshus Algorithmus und Ala. Weitere Bücher auf der "
            '<a href="https://www.amazon.de/s?i=stripbooks&amp;rh=p_27%3ASalomon%2BOwona" rel="noopener noreferrer" target="_blank" style="color: var(--accent);">Autorenseite bei Amazon</a>.</p>'
        )
    desc = c["desc"]
    url = f"{BASE}/shop/kategorie/{c['id']}"
    html = (
        head(f"{c['name']} | Shop | Salomon Owona", desc, url)
        + header("shop")
        + section(
            test_banner()
            + '\n                <p class="shop-crumbs"><a href="/de">Start</a> · <a href="/shop/">Shop</a> · '
            + esc(c["name"])
            + "</p>\n"
            + "                <h1>"
            + esc(c["name"])
            + "</h1>\n"
            + '                <p class="bio-text">'
            + esc(c["desc"])
            + "</p>\n"
            + "                "
            + chips(c["id"])
            + "\n                "
            + body
            + "\n                "
            + extra
        )
        + footer()
    )
    dest = SHOP / "kategorie" / f"{c['id']}.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def page_product(p):
    if p.get("type") == "collection":
        return
    url = f"{BASE}/shop/{p['slug']}"
    img = f"{BASE}{p['coverLg']}" if p.get("coverLg") else f"{BASE}/Salomon.webp"
    desc = (p.get("blurb") or p["title"])[:300]
    toc = ""
    if p.get("chapters"):
        lis = []
        for ch in p["chapters"]:
            w = ""
            if ch.get("words"):
                w = (
                    f'<span class="w">{ch["words"]:,} Wörter</span>'.replace(",", ".")
                )
            lis.append(f"<li><span>{esc(ch['title'])}</span>{w}</li>")
        toc = (
            "<h2>Inhalt</h2>\n                <ol class=\"shop-toc\">"
            + "".join(lis)
            + "</ol>"
        )
    notes = []
    if p.get("note"):
        notes.append(
            '<div class="values-box shop-draft"><p>' + esc(p["note"]) + "</p></div>"
        )
    if p.get("fulfillment") == "amazon":
        action = (
            f'<a class="contact-btn" href="{esc(p["amazonUrl"])}" rel="noopener noreferrer" target="_blank">Bei Amazon ansehen</a>'
        )
        price = '<p class="shop-muted">Preis und Lieferung bei Amazon.</p>'
    elif p.get("priceCents"):
        wc = ""
        if p.get("wordCount"):
            wc = f' ca. {p["wordCount"]:,} Wörter.'.replace(",", ".")
        price = (
            f'<p class="shop-price" style="font-size:1.3rem;margin:1rem 0 0.4rem">{euro(p["priceCents"])}</p>'
            f'<p class="shop-muted">E-Book (EPUB), {lang_label(p)}. Lieferung per E-Mail nach Zahlung.{wc}</p>'
        )
        if p.get("sellable"):
            note = (
                ""
                if is_live()
                else '<p class="shop-muted">Im Testmodus wird nichts berechnet.</p>'
            )
            action = (
                f'<button type="button" class="contact-btn" data-add="{esc(p["id"])}">In den Warenkorb</button>'
                '<a class="contact-btn" id="after-add" hidden href="/shop/warenkorb">Zum Warenkorb</a>'
                + note
            )
        else:
            coming = (
                f'<p class="shop-muted">{esc(p["badge"])}</p>'
                if p.get("badge")
                else '<p class="shop-muted">Coming soon</p>'
            )
            action = (
                '<button type="button" class="contact-btn" disabled>Derzeit nicht kaufbar</button>'
                + coming
            )
    else:
        action = ""
        price = ""
    words_meta = ""
    if p.get("wordCount"):
        words_meta = f'{p["wordCount"]} Wörter, {len(p.get("chapters") or [])} Kapitel'.replace(",", ".")
        # wordCount might be int; don't use comma thousands in German? 15836 is fine, or 15.836
        words_meta = f'{p["wordCount"]:,} Wörter, {len(p.get("chapters") or [])} Kapitel'.replace(",", ".")
    html = (
        head(
            f'{p["title"]} | Shop | Salomon Owona',
            desc,
            url,
            og_type="book",
            image=img,
            schema=schema_product(p),
        )
        + header("shop")
        + section(
            test_banner()
            + '\n                <p class="shop-crumbs"><a href="/de">Start</a> · <a href="/shop/">Shop</a> · '
            + f'<a href="/shop/kategorie/{p["category"]}">{esc(cat_by_id(p["category"])["name"])}</a> · '
            + esc(p["title"])
            + "</p>\n"
            + '                <article>\n'
            + '                    <div class="shop-pdp">\n'
            + f'                        {cover_html(p, lg=True)}\n'
            + "                        <div>\n"
            + f'                            <p class="shop-muted">{esc(cat_by_id(p["category"])["name"])}</p>\n'
            + f"                            <h1>{esc(p['title'])}</h1>\n"
            + (
                f'                            <p class="shop-muted" style="font-size:1.05rem;margin-top:-0.3rem">{esc(p["subtitle"])}</p>\n'
                if p.get("subtitle")
                else ""
            )
            + f'                            <p>Von {AUTHOR}. {esc(words_meta)}</p>\n'
            + '                            <span class="shop-ai">Mit Hilfe von KI erstellt</span>\n'
            + f"                            {price}\n"
            + f"                            {''.join(notes)}\n"
            + f'                            <div class="shop-actions">{action}</div>\n'
            + "                        </div>\n"
            + "                    </div>\n"
            + "                    <h2>Über dieses Buch</h2>\n"
            + "                    " + "".join(f'<p class="bio-text">{esc(para)}</p>\n' for para in (p.get("blurb") or "").split("\n\n") if para.strip()) + "\n"
            + f"                    {toc}\n"
            + f'                    <p class="shop-muted">Sprache: {lang_label(p)}. Weitere Sprachen erscheinen erst, wenn eine lektorierte Datei vorliegt.</p>\n'
            + "                </article>"
        )
        + footer()
    )
    (SHOP / f"{p['slug']}.html").write_text(html, encoding="utf-8")


def page_cart():
    html = (
        head("Warenkorb | Shop | Salomon Owona", "Warenkorb im Shop von Salomon Owona.", f"{BASE}/shop/warenkorb")
        + header("cart")
        + section(
            test_banner()
            + '\n                <p class="shop-crumbs"><a href="/shop/">Shop</a> · Warenkorb</p>\n'
            + "                <h1>Warenkorb</h1>\n"
            + '                <div id="cart-root"></div>'
        )
        + footer()
    )
    (SHOP / "warenkorb.html").write_text(html, encoding="utf-8")


def page_checkout():
    html = (
        head(
            "Kasse | Shop | Salomon Owona",
            (
                "Kasse im Shop von Salomon Owona. Zahlung mit Stripe (Euro) oder NotchPay (XAF)."
                if is_live()
                else "Kasse im Shop von Salomon Owona. Testmodus: keine echte Zahlung."
            ),
            f"{BASE}/shop/kasse",
        )
        + header("cart")
        + section(
            test_banner()
            + '\n                <p class="shop-crumbs"><a href="/shop/">Shop</a> · <a href="/shop/warenkorb">Warenkorb</a> · Kasse</p>\n'
            + "                <h1>Kasse</h1>\n"
            + (
                '                <p class="bio-text">Zahlung: Karte über Stripe in Euro oder MTN Mobile Money / Orange Money über NotchPay in CFA-Franc (XAF).</p>\n'
                if is_live()
                else '                <p class="bio-text">Zahlung wie im Shop von Owona Media: Karte über Stripe in Euro oder MTN Mobile Money / Orange Money über NotchPay in CFA-Franc (XAF). Im Testmodus wird der Ablauf nur simuliert.</p>\n'
            )
            + '                <div id="checkout-summary"></div>\n'
            + '                <form id="checkout-form" class="shop-form" novalidate>\n'
            + '                    <div class="shop-form-row">\n'
            + '                        <div><label for="firstName">Vorname</label><input id="firstName" name="firstName" type="text" autocomplete="given-name" required></div>\n'
            + '                        <div><label for="lastName">Nachname</label><input id="lastName" name="lastName" type="text" autocomplete="family-name" required></div>\n'
            + "                    </div>\n"
            + '                    <div><label for="email">E-Mail (für den Download-Link)</label><input id="email" name="email" type="email" autocomplete="email" required></div>\n'
            + '                    <div><label for="phone">Telefon (nötig für Mobile Money)</label><input id="phone" name="phone" type="tel" autocomplete="tel"></div>\n'
            + '                    <fieldset class="shop-pay">\n'
            + "                        <legend>Zahlungsart</legend>\n"
            + '                        <label class="shop-pay-opt"><input type="radio" name="pay" value="stripe" checked> Karte über Stripe (Euro)</label>\n'
            + '                        <label class="shop-pay-opt"><input type="radio" name="pay" value="momo" id="pay-momo"> MTN / Orange Money über NotchPay (XAF)</label>\n'
            + '                        <div id="momo-extra" hidden>\n'
            + '                            <label for="channel">Netzwerk</label>\n'
            + '                            <select id="channel" name="channel">\n'
            + '                                <option value="cm.mobile">MTN oder Orange</option>\n'
            + '                                <option value="cm.mtn">MTN Mobile Money</option>\n'
            + '                                <option value="cm.orange">Orange Money</option>\n'
            + "                            </select>\n"
            + "                        </div>\n"
            + "                    </fieldset>\n"
            + '                    <div class="shop-checks">\n'
            + (
                '                        <label><input type="checkbox" name="agb" required> Ich habe die <a href="/shop/agb" target="_blank">AGB</a> gelesen und erkenne sie an.</label>\n'
                if is_live()
                else '                        <label><input type="checkbox" name="agb" required> Ich habe die <a href="/shop/agb" target="_blank">AGB</a> gelesen und erkenne sie an. (Entwurf)</label>\n'
            )
            + '                        <label><input type="checkbox" name="privacy" required> Ich habe die <a href="/datenschutz" target="_blank">Datenschutzhinweise</a> gelesen.</label>\n'
            + '                        <label><input type="checkbox" name="widerruf" required> Ich stimme zu, dass mit der Erfüllung (Bereitstellung des E-Books) vor Ablauf der Widerrufsfrist begonnen wird, und mir ist bewusst, dass ich mein Widerrufsrecht mit Beginn der Erfüllung verliere. Hinweise: <a href="/shop/widerruf" target="_blank">Widerrufsbelehrung</a>.</label>\n'
            + "                    </div>\n"
            + '                    <p class="shop-err" data-error></p>\n'
            + (
                '                    <button class="contact-btn" type="submit">Zahlungspflichtig bestellen</button>\n'
                if is_live()
                else '                    <button class="contact-btn" type="submit">Testkauf simulieren</button>\n'
                  + '                    <p class="shop-muted">Es wird keine Zahlung ausgeführt. Der echte Verkauf bleibt ausgeschaltet, bis der Shop freigegeben ist und die Zahlungswege auf dem Server für diese Marke eingerichtet sind.</p>\n'
            )
            + "                </form>"
        )
        + footer()
    )
    (SHOP / "kasse.html").write_text(html, encoding="utf-8")


def page_thanks():
    html = (
        head(
            "Danke | Shop | Salomon Owona",
            "Bestellung im Shop von Salomon Owona." if is_live() else "Testbestellung im Shop von Salomon Owona.",
            f"{BASE}/shop/danke",
        )
        + header("shop")
        + section(
            test_banner()
            + (
                "\n                <h1>Danke für deine Bestellung</h1>\n"
                + "                <p>Wenn die Zahlung bestätigt ist, erhältst du den Download-Link per E-Mail an die angegebene Adresse.</p>\n"
                if is_live()
                else "\n                <h1>Testkauf abgeschlossen</h1>\n"
                + "                <p>Es wurde <strong>nichts berechnet</strong> und kein E-Book versendet. Der Ablauf der Kasse ist geprüft: Angaben, Einwilligungen und Warenkorb greifen.</p>\n"
                + "                <p>Sobald der Shop freigegeben ist, kommt nach einer echten Zahlung der Download-Link per E-Mail, so wie im Shop von Owona Media.</p>\n"
            )
            + '                <div class="shop-actions"><a class="contact-btn" href="/shop/">Zurück zum Shop</a></div>'
        )
        + footer()
    )
    (SHOP / "danke.html").write_text(html, encoding="utf-8")


AGB = r'''<h1>Allgemeine Geschäftsbedingungen</h1>
<div class="draft-banner">Stand: 12. November 2026. Text nach dem Vorbild der Texte auf owona.de, vom Anbieter zur Verwendung im Shop freigegeben. Kein Rechtsrat.</div>
<p>Stand: 12. November 2026. Anbieter im rechtlichen Sinn (nur in diesem Rechtstext): Salomon Firmin Owona, Ahornstrasse 52, 68542 Heddesheim, Deutschland, E-Mail: salomon@owona.de (öffentlich: Salomon Owona). Der Shop auf salomonowona.com verkauft digitale E-Books.</p>
<h2>1. Geltungsbereich</h2>
<p>Diese AGB gelten für den Erwerb digitaler Inhalte (E-Books im Format EPUB) über den Shop unter salomonowona.com. Abweichende Bedingungen des Kunden gelten nicht.</p>
<h2>2. Vertragsschluss</h2>
<p>Die Darstellung der Titel ist unverbindlich. Mit dem Absenden der Bestellung gibt der Kunde ein Angebot ab. Der Vertrag kommt zustande, wenn die Zahlung erfolgreich bestätigt ist und der Kunde eine Bestätigung per E-Mail erhält.</p>
<h2>3. Preise und Zahlung</h2>
<p>Preise verstehen sich in Euro inklusive der gesetzlichen Umsatzsteuer, soweit diese anfällt, und werden an der Kasse ausgewiesen. Zusätzlich kann per NotchPay mit MTN Mobile Money oder Orange Money in CFA-Franc (XAF) gezahlt werden; der Umrechnungskurs entspricht dem im Shop von Owona Media verwendeten Kurs und wird an der Kasse als Schätzung angezeigt. Karten- und ähnliche Zahlungen laufen über Stripe. Es gelten die Bedingungen der jeweiligen Zahlungsanbieter.</p>
<h2>4. Lieferung digitaler Inhalte</h2>
<p>Nach Zahlungseingang erhält der Kunde einen zeitlich begrenzten Download-Link per E-Mail an die angegebene Adresse. Es erfolgt keine Lieferung auf einem körperlichen Datenträger.</p>
<h2>5. Nutzungsrecht</h2>
<p>Der Kunde erhält ein einfaches, nicht übertragbares Recht, das E-Book für den eigenen persönlichen Gebrauch zu nutzen. Weitergabe, öffentliche Zugänglichmachung oder Bearbeitung sind nicht gestattet, soweit nicht gesetzlich erlaubt (z. B. nach UrhG).</p>
<h2>6. Widerrufsrecht</h2>
<p>Für digitale Inhalte gelten die gesetzlichen Widerrufsregeln sowie die in der Widerrufsbelehrung beschriebene Ausnahme, wenn der Kunde ausdrücklich zustimmt, dass mit der Erfüllung vor Fristablauf begonnen wird, und bestätigt, dass er sein Widerrufsrecht mit Beginn der Erfüllung verliert. Siehe <a href="/shop/widerruf">Widerrufsbelehrung</a>.</p>
<h2>7. KI-Hinweis</h2>
<p>Die angebotenen eigenen Titel sind mit Hilfe von KI erstellt. Der Hinweis steht auf den Produktseiten.</p>
<h2>8. Haftung</h2>
<p>Für Vorsatz und grobe Fahrlässigkeit sowie bei Verletzung von Leben, Körper und Gesundheit gilt die gesetzliche Haftung. Bei leichter Fahrlässigkeit wird nur für die Verletzung wesentlicher Vertragspflichten gehaftet, begrenzt auf den vorhersehbaren, vertragstypischen Schaden. Die Haftung nach dem Produkthaftungsgesetz bleibt unberührt.</p>
<h2>9. Schlussbestimmungen</h2>
<p>Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des UN-Kaufrechts. Ist der Kunde Verbraucher, bleiben zwingende Schutzvorschriften des Staates seines gewöhnlichen Aufenthalts unberührt. Sollten einzelne Klauseln unwirksam sein, bleibt der übrige Vertrag wirksam.</p>
'''

WIDERRUF = r'''<h1>Widerrufsbelehrung</h1>
<div class="draft-banner">Stand: 12. November 2026. Text nach dem Vorbild der Texte auf owona.de, vom Anbieter zur Verwendung im Shop freigegeben. Kein Rechtsrat.</div>
<p>Stand: 12. November 2026. Unternehmer: Salomon Firmin Owona, Ahornstrasse 52, 68542 Heddesheim, Deutschland, salomon@owona.de.</p>
<h2>Widerrufsrecht</h2>
<p>Sie haben das Recht, binnen vierzehn Tagen ohne Angabe von Gründen diesen Vertrag zu widerrufen. Die Widerrufsfrist beträgt vierzehn Tage ab dem Tag des Vertragsschlusses.</p>
<p>Um Ihr Widerrufsrecht auszuüben, müssen Sie uns (Salomon Firmin Owona, Ahornstrasse 52, 68542 Heddesheim, salomon@owona.de) mittels einer eindeutigen Erklärung (z. B. ein Brief oder eine E-Mail) über Ihren Entschluss informieren, diesen Vertrag zu widerrufen. Zur Wahrung der Frist reicht die rechtzeitige Absendung.</p>
<h2>Folgen des Widerrufs</h2>
<p>Wenn Sie diesen Vertrag widerrufen, haben wir Ihnen alle Zahlungen, die wir von Ihnen erhalten haben, unverzüglich und spätestens binnen vierzehn Tagen ab dem Tag zurückzuzahlen, an dem die Mitteilung über Ihren Widerruf bei uns eingegangen ist. Für die Rückzahlung verwenden wir dasselbe Zahlungsmittel, das Sie bei der ursprünglichen Transaktion eingesetzt haben, es sei denn, mit Ihnen wurde ausdrücklich etwas anderes vereinbart; es entstehen Ihnen wegen dieser Rückzahlung keine Entgelte.</p>
<h2>Besondere Hinweise für digitale Inhalte</h2>
<p>Das Widerrufsrecht erlischt bei einem Vertrag über die Lieferung von digitalen Inhalten, die nicht auf einem körperlichen Datenträger geliefert werden, wenn der Unternehmer mit der Erfüllung des Vertrags begonnen hat, nachdem der Verbraucher</p>
<ol>
  <li>ausdrücklich zugestimmt hat, dass der Unternehmer mit der Erfüllung des Vertrags vor Ablauf der Widerrufsfrist beginnt, und</li>
  <li>seine Kenntnis davon bestätigt hat, dass er durch seine Zustimmung mit Beginn der Erfüllung des Vertrags sein Widerrufsrecht verliert.</li>
</ol>
<p>An der Kasse wird diese Zustimmung und Bestätigung eingeholt, bevor ein E-Book bereitgestellt wird. Ohne sie wird – nach Freigabe des Shops – nicht vor Ablauf der Frist geliefert.</p>
<p>Muster-Widerrufsformular: An Salomon Firmin Owona, Ahornstrasse 52, 68542 Heddesheim, salomon@owona.de. Hiermit widerrufe(n) ich/wir den von mir/uns abgeschlossenen Vertrag über den Kauf der folgenden digitalen Inhalte: … Bestellt am … / Name / Anschrift / Datum / Unterschrift (nur bei Mitteilung auf Papier).</p>
'''


def legal_page(slug, title, body, desc):
    body = body.replace('class="draft-banner"', 'class="values-box shop-draft"')
    html = (
        head(f"{title} | Shop | Salomon Owona", desc, f"{BASE}/shop/{slug}")
        + header("shop")
        + section(
            '<p class="shop-crumbs"><a href="/shop/">Shop</a> · '
            + esc(title)
            + "</p>\n                "
            + body
        )
        + footer()
    )
    (SHOP / f"{slug}.html").write_text(html, encoding="utf-8")


FEATURED_SLUGS = [
    "vibe-coding-saas",
    "psychologie-e-commerce",
    "erziehung-im-wandel",
    "amazon-horus",
]


def featured_book_cards():
    cards = []
    for slug in FEATURED_SLUGS:
        try:
            p = product(slug)
        except StopIteration:
            continue
        cards.append(card(p))
    return "\n                    ".join(cards)


BUECHER = {
    "de.html": {
        "nav_after": '<a href="#projects">Projekte</a>',
        "nav_insert": '<a href="#projects">Projekte</a>\n            <a href="#buecher">Bücher</a>',
        "comment": "        <!-- 5b. Bücher -->",
        "h2": "Bücher",
        "lead": "E-Books von Salomon Owona – auf Deutsch, im gleichen Haus wie diese Seite. Der Shop ist angelegt, verkauft aber noch nicht.",
        "cta": "Zum Shop",
        "contact_comment": "        <!-- 6. Kontakt -->",
    },
    "en.html": {
        "nav_after": '<a href="#projects">Projects</a>',
        "nav_insert": '<a href="#projects">Projects</a>\n                    <a href="#buecher">Books</a>',
        "comment": "        <!-- 5b. Books -->",
        "h2": "Books",
        "lead": "E-books by Salomon Owona. The shop is in German and is part of this site. Sales start only after it is released.",
        "cta": "To the shop",
        "contact_comment": "        <!-- 6. Contact -->",
    },
    "fr.html": {
        "nav_after": '<a href="#projects">Projets</a>',
        "nav_insert": '<a href="#projects">Projets</a>\n                    <a href="#buecher">Livres</a>',
        "comment": "        <!-- 5b. Livres -->",
        "h2": "Livres",
        "lead": "Livres numériques de Salomon Owona. La boutique est en allemand et fait partie de ce site. La vente commencera seulement après sa mise en ligne.",
        "cta": "Vers la boutique",
        "contact_comment": "        <!-- 6. Contact -->",
    },
    "index.html": {
        "nav_after": '<a href="#projects">Miradi</a>',
        "nav_insert": '<a href="#projects">Miradi</a>\n            <a href="#buecher">Vitabu</a>',
        "comment": "        <!-- 5b. Vitabu -->",
        "h2": "Vitabu",
        "lead": "Vitabu vya Salomon Owona. Duka lipo kwa Kidachi na ni sehemu ya tovuti hii. Mauzo yataanza baada ya idhini.",
        "cta": "Nenda dukani",
        "contact_comment": "        <!-- 6. Kontakt -->",
    },
    "sw.html": {
        "nav_after": '<a href="#projects">Miradi</a>',
        "nav_insert": '<a href="#projects">Miradi</a>\n            <a href="#buecher">Vitabu</a>',
        "comment": "        <!-- 5b. Vitabu -->",
        "h2": "Vitabu",
        "lead": "Vitabu vya Salomon Owona. Duka lipo kwa Kidachi na ni sehemu ya tovuti hii. Mauzo yataanza baada ya idhini.",
        "cta": "Nenda dukani",
        "contact_comment": "        <!-- 6. Kontakt -->",
    },
}


def patch_buecher_section():
    """Add a Bücher/Books section on every language home page, matching #projects."""
    cards = featured_book_cards()
    for name, cfg in BUECHER.items():
        path = ROOT / name
        if not path.exists():
            continue
        t = path.read_text(encoding="utf-8")
        # sidebar link (idempotent — inspect the HTML nav, not the CSS class)
        if 'href="#buecher"' not in _sidebar_html(t):
            if cfg["nav_after"] in _sidebar_html(t):
                # replace only inside the nav
                nav = _sidebar_html(t)
                t = t.replace(nav, nav.replace(cfg["nav_after"], cfg["nav_insert"], 1), 1)
        block = (
                cfg["comment"] + "\n"
                '        <section id="buecher">\n'
                '            <div class="container-shifted">\n'
                f'                <h2>{cfg["h2"]}</h2>\n'
                f'                <p class="bio-text">{cfg["lead"]}</p>\n'
                '                <div class="project-grid">\n'
                f"                    {cards}\n"
                "                </div>\n"
                f'                <a href="/shop/" class="contact-btn">{cfg["cta"]}</a>\n'
                "            </div>\n"
                "        </section>\n\n"
            )
        if 'id="buecher"' in t:
            t = re.sub(
                r'(?:        <!-- 5b\.[^>]*-->\n)?        <section id="buecher">[\s\S]*?</section>\n\n',
                block,
                t,
                count=1,
            )
        else:
            marker = cfg["contact_comment"] + "\n        <section id=\"contact\">"
            alt = "        <section id=\"contact\">"
            if marker in t:
                t = t.replace(marker, block + marker, 1)
            elif alt in t:
                t = t.replace(alt, block + alt, 1)
            else:
                raise RuntimeError(f"cannot insert Bücher section into {name}")
        path.write_text(t, encoding="utf-8")



def _sidebar_html(t):
    m = re.search(r'<nav class="sidebar-nav">[\s\S]*?</nav>', t)
    return m.group(0) if m else ""


def _dedupe_sidebar_shop(t):
    def repl(m):
        block = m.group(0)
        prev = None
        while prev != block:
            prev = block
            block = re.sub(
                r'(<a href="[^"]+"[^>]*>[^<]*</a>)\s*\n\s*\1',
                r'\1',
                block,
            )
        return block
    return re.sub(r'<nav class="sidebar-nav">[\s\S]*?</nav>', repl, t, count=1)


def patch_site():
    """Add Shop links to existing language pages and footers; update sitemap, robots, llms, vercel, datenschutz."""
    # language sidebars
    replacements = [
        (ROOT / "de.html", '<a href="#contact">Kontakt</a>',
         '<a href="#contact">Kontakt</a>\n            <a href="/shop/">Shop</a>'),
        (ROOT / "en.html", '<a href="#contact">Contact</a>',
         '<a href="#contact">Contact</a>\n            <a href="/shop/">Shop (German)</a>'),
        (ROOT / "fr.html", '<a href="#contact">Contact</a>',
         '<a href="#contact">Contact</a>\n            <a href="/shop/">Boutique (en allemand)</a>'),
        (ROOT / "index.html", None, None),  # sw - detect
        (ROOT / "sw.html", None, None),
    ]
    for path, old, new in replacements:
        if not path.exists():
            continue
        t = path.read_text(encoding="utf-8")
        if old and old in t and 'href="/shop/"' not in _sidebar_html(t):
            t = t.replace(old, new, 1)
        # sw homepage
        if path.name in ("index.html", "sw.html"):
            t2 = t
            # typical sw contact link
            for cand in ('<a href="#contact">Mawasiliano</a>', '<a href="#contact">Kontakt</a>', '<a href="#contact">Contact</a>'):
                if cand in t2 and 'href="/shop/"' not in _sidebar_html(t2):
                    t2 = t2.replace(cand, cand + '\n            <a href="/shop/">Duka (Kidachi)</a>', 1)
                    break
            t = t2
        # footer legal-links
        if 'href="/shop/"' not in t[t.find("legal-links"):t.find("legal-links")+400] if "legal-links" in t else True:
            t = t.replace(
                '<a href="/impressum" style="color:var(--accent);">Impressum</a>',
                '<a href="/shop/" style="color:var(--accent);">Shop</a>\n                    <a href="/impressum" style="color:var(--accent);">Impressum</a>',
                1,
            )
            # EN/FR variants of footer
            t = t.replace(
                '<a href="/impressum"',
                '<a href="/shop/" style="color:var(--accent);">Shop</a>\n                    <a href="/impressum"',
                1,
            ) if 'href="/shop/"' not in t and '<a href="/impressum"' in t else t
        path.write_text(t, encoding="utf-8")

    # Avoid double shop links from the two replace attempts - clean later if needed

    # datenschutz: insert section before "Ihre Rechte" or "Aktualität"
    ds = ROOT / "datenschutz.html"
    t = ds.read_text(encoding="utf-8")
    if "Stripe" not in t:
        section = """
        <div class="draft-banner" style="border:1px dashed #e07a5f;background:rgba(224,122,95,0.08);color:#f0c8bc;padding:0.85rem 1rem;border-radius:8px;margin:1rem 0;">
            Abschnitt zum Shop auf salomonowona.com, Stand 12. November 2026.
        </div>
        <h2>7a. Shop, Stripe und NotchPay</h2>
        <p>Wenn Sie im Shop ein E-Book bestellen, verarbeiten wir die von Ihnen angegebenen Daten (Name, E-Mail, gegebenenfalls Telefonnummer und Anschrift) zur Vertragserfüllung (Art. 6 Abs. 1 lit. b DSGVO), zur Lieferung des Download-Links und zur gesetzlichen Aufbewahrung von Rechnungen (Art. 6 Abs. 1 lit. c DSGVO).</p>
        <ul>
            <li><strong style="color:var(--text-main)">Stripe</strong> – Zahlungen mit Karte in Euro. Stripe ist ein Zahlungsdienstleister (Stripe Payments Europe, soweit anwendbar, mit möglichen Übermittlungen in die USA auf Grundlage geeigneter Garantien, etwa Standardvertragsklauseln bzw. EU-US Data Privacy Framework). Es gelten die Hinweise von <a href="https://stripe.com/privacy" target="_blank" rel="noopener noreferrer">Stripe</a>.</li>
            <li><strong style="color:var(--text-main)">NotchPay</strong> – Zahlungen mit MTN Mobile Money und Orange Money in CFA-Franc (XAF). Dabei werden Zahlungs- und Kontaktdaten an NotchPay übermittelt. Es gelten die Hinweise des Anbieters.</li>
        </ul>
"""
        t = t.replace("<h2>7. Ihre Rechte</h2>", section + "\n        <h2>7. Ihre Rechte</h2>", 1)
        t = t.replace("Stand dieser Hinweise: 20. Oktober 2026.", "Stand dieser Hinweise: 12. November 2026.", 1)
        ds.write_text(t, encoding="utf-8")

    # sitemap
    sm = ROOT / "sitemap.xml"
    xml = sm.read_text(encoding="utf-8")
    urls = [
        f"{BASE}/shop/",
        f"{BASE}/shop/warenkorb",
        f"{BASE}/shop/kasse",
        f"{BASE}/shop/agb",
        f"{BASE}/shop/widerruf",
    ]
    for c in CATEGORIES:
        urls.append(f"{BASE}/shop/kategorie/{c['id']}")
    for p in PRODUCTS:
        if p.get("type") != "collection":
            urls.append(f"{BASE}/shop/{p['slug']}")
    # rebuild keep existing, append shop if missing
    for u in urls:
        if f"<loc>{u}</loc>" not in xml:
            xml = xml.replace("</urlset>", f"  <url><loc>{u}</loc></url>\n</urlset>")
    sm.write_text(xml, encoding="utf-8")

    # llms.txt
    ll = ROOT / "llms.txt"
    t = ll.read_text(encoding="utf-8")
    if "/shop/" not in t:
        t += """
## Shop

E-Book-Shop von Salomon Owona. Zahlung wie im Shop von Owona Media: Stripe (Euro) und NotchPay / MTN / Orange Money (XAF). Kaufbar sind derzeit die lektorierten Titel 197–204. 205, 235 und 236 sind sichtbar, aber noch nicht kaufbar. Die fünf Titel des Owona-Media-Shops (230–234) und CSEB-Titel sind hier nicht enthalten.

- [Shop](https://salomonowona.com/shop/)
- [AGB](https://salomonowona.com/shop/agb)
- [Widerruf](https://salomonowona.com/shop/widerruf)
"""
        for c in CATEGORIES:
            t += f"- [{c['name']}](https://salomonowona.com/shop/kategorie/{c['id']})\n"
        for p in PRODUCTS:
            if p.get("type") != "collection":
                t += f"- [{p['title']}](https://salomonowona.com/shop/{p['slug']})\n"
        ll.write_text(t, encoding="utf-8")

    # vercel.json: rewrites + CSP connect-src
    import json as _json
    vpath = ROOT / "vercel.json"
    v = _json.loads(vpath.read_text(encoding="utf-8"))
    new_rewrites = [
        {"source": "/shop", "destination": "/shop/index.html"},
        {"source": "/shop/", "destination": "/shop/index.html"},
        {"source": "/shop/warenkorb", "destination": "/shop/warenkorb.html"},
        {"source": "/shop/warenkorb/", "destination": "/shop/warenkorb.html"},
        {"source": "/shop/kasse", "destination": "/shop/kasse.html"},
        {"source": "/shop/kasse/", "destination": "/shop/kasse.html"},
        {"source": "/shop/danke", "destination": "/shop/danke.html"},
        {"source": "/shop/danke/", "destination": "/shop/danke.html"},
        {"source": "/shop/agb", "destination": "/shop/agb.html"},
        {"source": "/shop/agb/", "destination": "/shop/agb.html"},
        {"source": "/shop/widerruf", "destination": "/shop/widerruf.html"},
        {"source": "/shop/widerruf/", "destination": "/shop/widerruf.html"},
    ]
    for c in CATEGORIES:
        new_rewrites.append({"source": f"/shop/kategorie/{c['id']}", "destination": f"/shop/kategorie/{c['id']}.html"})
        new_rewrites.append({"source": f"/shop/kategorie/{c['id']}/", "destination": f"/shop/kategorie/{c['id']}.html"})
    for p in PRODUCTS:
        if p.get("type") == "collection":
            continue
        new_rewrites.append({"source": f"/shop/{p['slug']}", "destination": f"/shop/{p['slug']}.html"})
        new_rewrites.append({"source": f"/shop/{p['slug']}/", "destination": f"/shop/{p['slug']}.html"})
    existing_src = {r["source"] for r in v.get("rewrites", [])}
    for r in new_rewrites:
        if r["source"] not in existing_src:
            v.setdefault("rewrites", []).append(r)
            existing_src.add(r["source"])
    # CSP
    for block in v.get("headers", []):
        for h in block.get("headers", []):
            if h.get("key") == "Content-Security-Policy":
                val = h["value"]
                for src in ("https://owona.de", "https://api.owonamedia.de"):
                    if src not in val:
                        val = val.replace(
                            "connect-src 'self' https://radio.owonamedia.de https://stats.owona.de",
                            "connect-src 'self' https://radio.owonamedia.de https://stats.owona.de " + src,
                        )
                h["value"] = val
    vpath.write_text(_json.dumps(v, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    patch_buecher_section()


def main():
    page_index()
    for c in CATEGORIES:
        page_category(c)
    for p in PRODUCTS:
        page_product(p)
    page_cart()
    page_checkout()
    page_thanks()
    legal_page("agb", "AGB", AGB, "Allgemeine Geschäftsbedingungen des Shops von Salomon Owona.")
    legal_page("widerruf", "Widerrufsbelehrung", WIDERRUF, "Widerrufsbelehrung für digitale Inhalte im Shop von Salomon Owona.")
    patch_site()
    print("generated shop pages ok")


if __name__ == "__main__":
    main()

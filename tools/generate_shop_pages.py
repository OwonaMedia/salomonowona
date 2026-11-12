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
            }
            for p in PRODUCTS
        ],
    },
    ensure_ascii=False,
    separators=(",", ":"),
)


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
    <link rel="stylesheet" href="/shop/shop.css">
    <script>window.SO_SHOP={SHOP_JSON};</script>
    {schema or ""}
    {extra}
</head>
"""


def header(current="shop"):
    def cur(name):
        return ' aria-current="page"' if current == name else ""

    return f"""<body>
<header class="shop-header">
  <div class="nav-inner">
    <a class="logo" href="/">Salomon Owona</a>
    <nav class="nav-links" aria-label="Shop-Navigation">
      <a href="/de">Website</a>
      <a href="/shop/"{cur("shop")}>Shop</a>
      <a class="cart-link" href="/shop/warenkorb"{cur("cart")}>Warenkorb <span class="cart-badge" data-cart-count>0</span></a>
    </nav>
  </div>
</header>
"""


def footer():
    return f"""<footer class="shop-footer">
  <div class="wrap">
    <nav class="legal-links" aria-label="Rechtliches">
      <a href="/shop/">Shop</a>
      <a href="/impressum">Impressum</a>
      <a href="/datenschutz">Datenschutz</a>
      <a href="/shop/agb">AGB</a>
      <a href="/shop/widerruf">Widerruf</a>
    </nav>
    <p>Öffentlicher Name: Salomon Owona. Der Shop ist auf Deutsch. Weitere Sprachen erst, wenn eine lektorierte Datei vorliegt.</p>
    <p>&copy; 1981–2026 Salomon Owona. Zwischen Welten.</p>
  </div>
</footer>
<script src="/shop/shop.js" defer></script>
{GOAT}
</body>
</html>
"""


def test_banner():
    return """<div class="banner" role="status">
  <strong>Testmodus.</strong>
  Der Shop ist angelegt, verkauft aber noch nicht. Es wird nichts berechnet, und es geht keine Bestellung hinaus.
  Der Verkauf startet erst, wenn Salomon Owona den Shop ausdrücklich freigibt.
</div>"""


def chips(active=None):
    bits = ['<a class="chip%s" href="/shop/"%s>Alle</a>' % (" is-active" if not active else "", ' aria-current="page"' if not active else "")]
    for c in CATEGORIES:
        is_a = active == c["id"]
        bits.append(
            f'<a class="chip{" is-active" if is_a else ""}" href="/shop/kategorie/{c["id"]}"'
            f'{" aria-current=\"page\"" if is_a else ""}>{esc(c["short"])}</a>'
        )
    return '<nav class="chips" aria-label="Kategorien">' + "".join(bits) + "</nav>"


def cover_html(p, lg=False, cls="card-cover"):
    title = esc(p["title"])
    if p.get("cover"):
        src = p["coverLg"] if lg and p.get("coverLg") else p["cover"]
        jpg = p.get("coverLgJpg") if lg and p.get("coverLgJpg") else p.get("coverJpg")
        return f'''<div class="{cls}">
          {badge(p)}
          <picture>
            <source type="image/webp" srcset="{esc(src)}">
            <img src="{esc(jpg or src)}" alt="Cover: {title}" width="400" height="640">
          </picture>
        </div>'''
    return f'<div class="{cls}">{badge(p)}<div class="placeholder">{title}</div></div>'


def badge(p):
    if p.get("badge"):
        return f'<span class="badge">{esc(p["badge"])}</span>'
    return ""


def card(p):
    price = f'<span class="price">{euro(p["priceCents"])}</span>' if p.get("priceCents") else '<span class="muted">Bei Amazon</span>'
    words = f' · ca. {p["wordCount"]:,} Wörter'.replace(",", ".") if p.get("wordCount") else ""
    cat = cat_by_id(p["category"])["short"]
    return f'''<a class="card" href="/shop/{esc(p["slug"])}">
      {cover_html(p)}
      <div class="card-body">
        <div class="card-cat">{esc(cat)}</div>
        <h3 class="card-title">{esc(p["title"])}</h3>
        <div class="card-meta">{price}{words}</div>
      </div>
    </a>'''


def schema_product(p):
    if p.get("type") == "collection":
        return ""
    url = f"{BASE}/shop/{p['slug']}"
    img = f"{BASE}{p['coverLg']}" if p.get("coverLg") else f"{BASE}/Salomon.webp"
    avail = "https://schema.org/PreOrder"  # honest: shop not live
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
        "inLanguage": "de",
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
            f'''<a class="cat-tile" href="/shop/kategorie/{c["id"]}">
              <h3>{esc(c["name"])}</h3>
              <p>{esc(c["desc"])}</p>
              <div class="n">{esc(label)}</div>
            </a>'''
        )
    own = [p for p in PRODUCTS if p["fulfillment"] == "own"]
    cards = "\n".join(card(p) for p in own)
    amazon = [p for p in PRODUCTS if p["fulfillment"] == "amazon" and p.get("type") != "collection"]
    acards = "\n".join(card(p) for p in amazon)
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
        head("Shop | Salomon Owona", desc, f"{BASE}/shop/", schema='<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + "</script>")
        + header("shop")
        + f"""<main>
  <div class="wrap">
    {test_banner()}
    <p class="breadcrumbs"><a href="/de">Start</a> · Shop</p>
    <h1>Shop</h1>
    <p class="muted">E-Books von {AUTHOR}. Nur Deutsch, nur wo eine geprüfte Datei vorliegt. Digitale Lieferungen per E-Mail, Zahlung wie im Shop von Owona Media: Karte über Stripe in Euro oder MTN/Orange Money über NotchPay in CFA-Franc.</p>
    <p class="ai-notice">Alle eigenen Titel: Mit Hilfe von KI erstellt.</p>
    {chips()}
    <h2>Kategorien</h2>
    <div class="cats-overview">{''.join(tiles)}</div>
    <h2>Eigene Titel</h2>
    <div class="grid">{cards}</div>
    <h2>Afro-Mythologie bei Amazon</h2>
    <p class="muted">Diese Titel haben keine eigene Shop-Datei; der Kauf erfolgt über Amazon.</p>
    <div class="grid">{acards}</div>
  </div>
</main>
"""
        + footer()
    )
    (SHOP / "index.html").write_text(html, encoding="utf-8")


def page_category(c):
    items = products_in(c["id"])
    if items:
        body = '<div class="grid">' + "\n".join(card(p) for p in items) + "</div>"
    else:
        body = (
            f'<div class="empty"><p>In <strong>{esc(c["name"])}</strong> sind noch keine eigenen Titel im Katalog. '
            "Weitere Bücher sind in Vorbereitung und erscheinen hier, sobald eine lektorierte deutsche Fassung vorliegt.</p></div>"
        )
    extra = ""
    if c["id"] == "afro-mythologie":
        extra = (
            '<p class="muted" style="margin-top:1.5rem">Vier Amazon-Listings sind über gesicherte Kurzlinks bestätigt '
            "(Horus, Ra, Eshus Algorithmus, Ala). Ein fünftes Amazon-Mythologie-Listing konnte ohne Bestätigung nicht eindeutig "
            "zugeordnet werden. Weitere Titel: "
            '<a href="https://www.amazon.de/s?i=stripbooks&amp;rh=p_27%3ASalomon%2BOwona" rel="noopener noreferrer" target="_blank">Autorenseite bei Amazon</a>.</p>'
        )
    desc = c["desc"]
    url = f"{BASE}/shop/kategorie/{c['id']}"
    html = (
        head(f"{c['name']} | Shop | Salomon Owona", desc, url)
        + header("shop")
        + f"""<main>
  <div class="wrap">
    {test_banner()}
    <p class="breadcrumbs"><a href="/de">Start</a> · <a href="/shop/">Shop</a> · {esc(c["name"])}</p>
    <h1>{esc(c["name"])}</h1>
    <p class="muted">{esc(c["desc"])}</p>
    {chips(c["id"])}
    {body}
    {extra}
  </div>
</main>
"""
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
            w = f'<span class="w">{ch["words"]:,} Wörter</span>'.replace(",", ".") if ch.get("words") else ""
            lis.append(f'<li><span>{esc(ch["title"])}</span>{w}</li>')
        toc = "<h2>Inhalt</h2><ol class=\"toc\">" + "".join(lis) + "</ol>"
    notes = []
    if p.get("note"):
        notes.append(f'<div class="banner banner-warn">{esc(p["note"])}</div>')
    if p.get("fulfillment") == "amazon":
        action = f'<a class="btn" href="{esc(p["amazonUrl"])}" rel="noopener noreferrer" target="_blank">Bei Amazon ansehen</a>'
        price = "<p class=\"muted\">Preis und Lieferung bei Amazon.</p>"
    elif p.get("priceCents"):
        price = f'<p class="price" style="font-size:1.4rem">{euro(p["priceCents"])}</p><p class="muted">E-Book (EPUB), Deutsch. Lieferung per E-Mail nach Zahlung. ca. {p["wordCount"]:,} Wörter.</p>'.replace(",", ".")
        if p.get("sellable"):
            action = (
                f'<button type="button" class="btn" data-add="{esc(p["id"])}">In den Warenkorb</button>'
                '<a class="btn btn-ghost" id="after-add" hidden href="/shop/warenkorb">Zum Warenkorb</a>'
                '<p class="muted">Im Testmodus wird nichts berechnet.</p>'
            )
        else:
            action = '<button type="button" class="btn" disabled>Derzeit nicht kaufbar</button>'
    else:
        action = ""
        price = ""
    words_meta = f'{p["wordCount"]} Wörter, {len(p.get("chapters") or [])} Kapitel' if p.get("wordCount") else ""
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
        + f"""<main>
  <div class="wrap">
    {test_banner()}
    <p class="breadcrumbs"><a href="/de">Start</a> · <a href="/shop/">Shop</a> · <a href="/shop/kategorie/{p["category"]}">{esc(cat_by_id(p["category"])["name"])}</a> · {esc(p["title"])}</p>
    <article class="pdp">
      {cover_html(p, lg=True, cls="pdp-cover")}
      <div>
        <p class="card-cat">{esc(cat_by_id(p["category"])["name"])}</p>
        <h1>{esc(p["title"])}</h1>
        <p>Von {AUTHOR}. {esc(words_meta)}</p>
        <span class="ai-notice">Mit Hilfe von KI erstellt</span>
        {price}
        {''.join(notes)}
        <div class="actions">{action}</div>
        <h2>Über dieses Buch</h2>
        <p>{esc(p.get("blurb") or "")}</p>
        {toc}
        <p class="muted">Sprache: Deutsch. Weitere Sprachen erscheinen erst, wenn eine lektorierte Datei vorliegt.</p>
      </div>
    </article>
  </div>
</main>
"""
        + footer()
    )
    (SHOP / f"{p['slug']}.html").write_text(html, encoding="utf-8")


def page_cart():
    html = (
        head("Warenkorb | Shop | Salomon Owona", "Warenkorb im Shop von Salomon Owona.", f"{BASE}/shop/warenkorb")
        + header("cart")
        + f"""<main>
  <div class="wrap-narrow">
    {test_banner()}
    <p class="breadcrumbs"><a href="/shop/">Shop</a> · Warenkorb</p>
    <h1>Warenkorb</h1>
    <div id="cart-root"></div>
  </div>
</main>
"""
        + footer()
    )
    (SHOP / "warenkorb.html").write_text(html, encoding="utf-8")


def page_checkout():
    html = (
        head("Kasse | Shop | Salomon Owona", "Kasse im Shop von Salomon Owona. Testmodus: keine echte Zahlung.", f"{BASE}/shop/kasse")
        + header("cart")
        + f"""<main>
  <div class="wrap-narrow">
    {test_banner()}
    <p class="breadcrumbs"><a href="/shop/">Shop</a> · <a href="/shop/warenkorb">Warenkorb</a> · Kasse</p>
    <h1>Kasse</h1>
    <p class="muted">Zahlung wie im Shop von Owona Media: Karte über Stripe in Euro oder MTN Mobile Money / Orange Money über NotchPay in CFA-Franc (XAF). Im Testmodus wird der Ablauf nur simuliert.</p>
    <div id="checkout-summary"></div>
    <form id="checkout-form" class="form" novalidate>
      <div class="form-row">
        <div><label for="firstName">Vorname</label><input id="firstName" name="firstName" type="text" autocomplete="given-name" required></div>
        <div><label for="lastName">Nachname</label><input id="lastName" name="lastName" type="text" autocomplete="family-name" required></div>
      </div>
      <div><label for="email">E-Mail (für den Download-Link)</label><input id="email" name="email" type="email" autocomplete="email" required></div>
      <div><label for="phone">Telefon (nötig für Mobile Money)</label><input id="phone" name="phone" type="tel" autocomplete="tel"></div>
      <fieldset class="pay-opts">
        <legend>Zahlungsart</legend>
        <label class="pay-opt"><input type="radio" name="pay" value="stripe" checked> Karte über Stripe (Euro)</label>
        <label class="pay-opt"><input type="radio" name="pay" value="momo" id="pay-momo"> MTN / Orange Money über NotchPay (XAF)</label>
        <div id="momo-extra" hidden>
          <label for="channel">Netzwerk</label>
          <select id="channel" name="channel">
            <option value="cm.mobile">MTN oder Orange</option>
            <option value="cm.mtn">MTN Mobile Money</option>
            <option value="cm.orange">Orange Money</option>
          </select>
        </div>
      </fieldset>
      <div class="checks">
        <label><input type="checkbox" name="agb" required> Ich habe die <a href="/shop/agb" target="_blank">AGB</a> gelesen und erkenne sie an. (Entwurf)</label>
        <label><input type="checkbox" name="privacy" required> Ich habe die <a href="/datenschutz" target="_blank">Datenschutzhinweise</a> gelesen.</label>
        <label><input type="checkbox" name="widerruf" required> Ich stimme zu, dass mit der Erfüllung (Bereitstellung des E-Books) vor Ablauf der Widerrufsfrist begonnen wird, und mir ist bewusst, dass ich mein Widerrufsrecht mit Beginn der Erfüllung verliere. Hinweise: <a href="/shop/widerruf" target="_blank">Widerrufsbelehrung</a>.</label>
      </div>
      <p class="err" data-error></p>
      <button class="btn" type="submit">Testkauf simulieren</button>
      <p class="muted">Es wird keine Zahlung ausgeführt. Der echte Verkauf bleibt ausgeschaltet, bis der Shop freigegeben ist und die Zahlungswege auf dem Server für diese Marke eingerichtet sind.</p>
    </form>
  </div>
</main>
"""
        + footer()
    )
    (SHOP / "kasse.html").write_text(html, encoding="utf-8")


def page_thanks():
    html = (
        head("Danke | Shop | Salomon Owona", "Testbestellung im Shop von Salomon Owona.", f"{BASE}/shop/danke")
        + header("shop")
        + f"""<main>
  <div class="wrap-narrow">
    {test_banner()}
    <h1>Testkauf abgeschlossen</h1>
    <p>Es wurde <strong>nichts berechnet</strong> und kein E-Book versendet. Der Ablauf der Kasse ist geprüft: Angaben, Einwilligungen und Warenkorb greifen.</p>
    <p>Sobald der Shop freigegeben ist, kommt nach einer echten Zahlung der Download-Link per E-Mail, so wie im Shop von Owona Media.</p>
    <div class="actions"><a class="btn" href="/shop/">Zurück zum Shop</a></div>
  </div>
</main>
"""
        + footer()
    )
    (SHOP / "danke.html").write_text(html, encoding="utf-8")


AGB = r'''<h1>Allgemeine Geschäftsbedingungen</h1>
<div class="draft-banner"><strong>Entwurf – rechtliche Prüfung nötig.</strong> Dieser Text ist ein Arbeitsentwurf nach dem Vorbild der Texte auf owona.de. Er ist kein Rechtsrat und nicht zur Verwendung im echten Verkauf bestimmt, solange er nicht geprüft und freigegeben ist.</div>
<p>Stand des Entwurfs: 12. November 2026. Anbieter im rechtlichen Sinn (nur in diesem Rechtstext): Salomon Firmin Owona, Ahornstrasse 52, 68542 Heddesheim, Deutschland, E-Mail: salomon@owona.de (öffentlich: Salomon Owona). Der Shop auf salomonowona.com verkauft digitale E-Books.</p>
<h2>1. Geltungsbereich</h2>
<p>Diese AGB gelten für den Erwerb digitaler Inhalte (E-Books im Format EPUB) über den Shop unter salomonowona.com. Abweichende Bedingungen des Kunden gelten nicht.</p>
<h2>2. Vertragsschluss</h2>
<p>Die Darstellung der Titel ist unverbindlich. Mit dem Absenden der Bestellung gibt der Kunde ein Angebot ab. Der Vertrag kommt zustande, wenn die Zahlung erfolgreich bestätigt ist und der Kunde eine Bestätigung per E-Mail erhält. Im Testmodus kommt kein Vertrag zustande.</p>
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
<div class="draft-banner"><strong>Entwurf – rechtliche Prüfung nötig.</strong> Arbeitsentwurf für digitale Inhalte nach dem Vorbild der Texte auf owona.de. Nicht zur Verwendung im echten Verkauf, solange er nicht geprüft und freigegeben ist.</div>
<p>Stand des Entwurfs: 12. November 2026. Unternehmer: Salomon Firmin Owona, Ahornstrasse 52, 68542 Heddesheim, Deutschland, salomon@owona.de.</p>
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
    html = (
        head(f"{title} | Shop | Salomon Owona", desc, f"{BASE}/shop/{slug}")
        + header("shop")
        + f"""<main>
  <div class="wrap-narrow">
    <p class="breadcrumbs"><a href="/shop/">Shop</a> · {esc(title)}</p>
    {body}
  </div>
</main>
"""
        + footer()
    )
    (SHOP / f"{slug}.html").write_text(html, encoding="utf-8")


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
        if "/shop/" in t and "sidebar-nav" in t and t.count('href="/shop/"') >= 1 and "Shop" in t[t.find("sidebar-nav"):t.find("sidebar-nav")+800]:
            pass  # may still need insert
        if old and old in t and 'href="/shop/"' not in t[t.find("sidebar-nav"):t.find("sidebar-nav")+600]:
            t = t.replace(old, new, 1)
        # sw homepage
        if path.name in ("index.html", "sw.html"):
            t2 = t
            # typical sw contact link
            for cand in ('<a href="#contact">Mawasiliano</a>', '<a href="#contact">Kontakt</a>', '<a href="#contact">Contact</a>'):
                if cand in t2 and 'href="/shop/"' not in t2[t2.find("sidebar-nav"):t2.find("sidebar-nav")+600]:
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
            <strong>Entwurf – rechtliche Prüfung nötig.</strong> Der folgende Abschnitt betrifft den geplanten Shop und gilt für echte Bestellungen erst nach Freigabe und Prüfung.
        </div>
        <h2>7a. Shop, Stripe und NotchPay (Entwurf)</h2>
        <p>Wenn Sie im Shop ein E-Book bestellen, verarbeiten wir die von Ihnen angegebenen Daten (Name, E-Mail, gegebenenfalls Telefonnummer und Anschrift) zur Vertragserfüllung (Art. 6 Abs. 1 lit. b DSGVO), zur Lieferung des Download-Links und zur gesetzlichen Aufbewahrung von Rechnungen (Art. 6 Abs. 1 lit. c DSGVO).</p>
        <ul>
            <li><strong style="color:var(--text-main)">Stripe</strong> – Zahlungen mit Karte in Euro. Stripe ist ein Zahlungsdienstleister (Stripe Payments Europe, soweit anwendbar, mit möglichen Übermittlungen in die USA auf Grundlage geeigneter Garantien, etwa Standardvertragsklauseln bzw. EU-US Data Privacy Framework). Es gelten die Hinweise von <a href="https://stripe.com/privacy" target="_blank" rel="noopener noreferrer">Stripe</a>.</li>
            <li><strong style="color:var(--text-main)">NotchPay</strong> – Zahlungen mit MTN Mobile Money und Orange Money in CFA-Franc (XAF). Dabei werden Zahlungs- und Kontaktdaten an NotchPay übermittelt. Es gelten die Hinweise des Anbieters.</li>
        </ul>
        <p>Im Testmodus des Shops werden keine Zahlungen ausgeführt und keine Bestellungen erfüllt. Eine Speicherung von Testdaten erfolgt allenfalls vorübergehend in Ihrem Browser (Warenkorb).</p>
"""
        t = t.replace("<h2>7. Ihre Rechte</h2>", section + "\n        <h2>7. Ihre Rechte</h2>", 1)
        t = t.replace("Stand dieser Hinweise: 20. Oktober 2026.", "Stand dieser Hinweise: 12. November 2026 (Entwurf Shop-Abschnitt).", 1)
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

E-Book-Shop von Salomon Owona auf Deutsch (Testmodus, Verkauf erst nach Freigabe). Zahlung geplant wie im Shop von Owona Media: Stripe (Euro) und NotchPay / MTN / Orange Money (XAF). Die fünf Titel des Owona-Media-Shops (230–234) und CSEB-Titel sind hier nicht enthalten.

- [Shop](https://salomonowona.com/shop/)
- [AGB (Entwurf)](https://salomonowona.com/shop/agb)
- [Widerruf (Entwurf)](https://salomonowona.com/shop/widerruf)
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


def main():
    page_index()
    for c in CATEGORIES:
        page_category(c)
    for p in PRODUCTS:
        page_product(p)
    page_cart()
    page_checkout()
    page_thanks()
    legal_page("agb", "AGB", AGB, "Allgemeine Geschäftsbedingungen (Entwurf) des Shops von Salomon Owona.")
    legal_page("widerruf", "Widerrufsbelehrung", WIDERRUF, "Widerrufsbelehrung (Entwurf) für digitale Inhalte im Shop von Salomon Owona.")
    patch_site()
    print("generated shop pages ok")


if __name__ == "__main__":
    main()

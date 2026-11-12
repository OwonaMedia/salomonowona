# Shop salomonowona.com

Stand: 12. November 2026. Der Shop geht mit Firmins Go live: kaufbar sind 197–204 zu 4,99 € (3.268 XAF). 205, 235 und 236 bleiben sichtbar, aber nicht kaufbar.

## Architektur

- **Frontend:** statisches HTML im bestehenden Repo. Der Shop ist **kein eigenes Theme**, sondern nutzt dieselbe Chrome wie die übrige Seite: `style#page-style` und Tailwind aus `de.html`, fester Header (Logo, Salomon Radio, Hamburger), Sidebar mit Sprachumschalter, Fußzeile mit Patreon und Social, Abschnitte in `.container-shifted`, Bücher als `.project-card`, Aktionen als `.contact-btn`. `shop/shop.css` enthält nur Formular- und Tabellenregeln mit denselben Tokens. Auf den Sprach-Startseiten gibt es die Sektion `#buecher`; der Shop bleibt über die Hauptnavigation erreichbar. Kein Vite, kein zweites Framework. Produktseiten sind echte Dateien mit schema.org (`Book` + `Product` + `Offer`), damit Suche und LLMs sie lesen können. `sitemap.xml`, `llms.txt` und `robots.txt` sind ergänzt.
- **Zahlung:** derselbe **om-api**-Stack wie der Shop auf owona.de (Stripe-Karte in EUR, NotchPay mit MTN/Orange Money in XAF, Kurs 655). Das Frontend spricht nach Freigabe `https://owona.de/api/…` mit `shop=salomonowona`. Die API-Erweiterung liegt im Repo OwonaMedia/OM. Der Server-Schalter `SO_SHOP_ENABLED` muss auf dem Produktivserver genau `1` sein, sonst antwortet der Checkout mit 403.
- **Erfüllung:** jeder kaufbare Titel ist fest an eine Archiv-ID gebunden (`ebook_id`). Der Server darf daraus kein neues Buch erzeugen. Lieferung per E-Mail-Download wie im OM-Shop, nur Deutsch.
- **Feature-Flag:** `shopLive: true` im Frontend (`shop/products.json`) schaltet die echte Kasse frei. Die API lehnt ohne `SO_SHOP_ENABLED=1` weiterhin mit 403 ab.

## Katalog

Acht Kategorien: Herkunft & Migration, Musik & Beats, Liebe & Familie, E-Commerce, Krypto, Vibe Coding & KI, Geschichte & Rassismus, Afro-Mythologie.

- Eigene Dateien: 235, 236, 197–205. **Nicht** enthalten: OM-Shop 230–234, CSEB, zurückgezogenes 169, sensible 211/212.
- 197–204: lektorierte deutsche Fassungen, Shoppreis **4,99 €** (3.268 XAF bei Kurs 655, gerundet wie im OM-Shop).
- 235 und 236: Manuskript fertig, **Lektorat ausstehend**, sichtbar, nicht kaufbar. Preis bereits hinterlegt: **14,99 €** (9.818 XAF).
- 205: Titel **Networks of Neocolonialism**, Sprache `en`, Preis **4,99 €** (3.268 XAF) hinterlegt, **nicht kaufbar** (Coming soon / „Derzeit nicht kaufbar“). Im Archiv gibt es kein EPUB mit diesem englischen Titel; die Titelprüfung der Erfüllung würde scheitern. Der frühere deutsche Archivtitel war „Die Netzwerke des Neokolonialismus (Lektorat)“.
- Afro-Mythologie bei Amazon (keine eigene Datei, Link zu Amazon): genau vier Titel — Horus (B0GSSFG63W), Ra (B0GSWT8YYT), Eshus Algorithmus (B0GHQ3L38Y), Ala (B0GTFPY8D3).

## Rechtstexte

AGB und Widerruf unter `/shop/agb` und `/shop/widerruf` sowie ein Abschnitt zu Stripe/NotchPay in der Datenschutzerklärung sind **Entwürfe – rechtliche Prüfung nötig**. Der Widerruf für digitale Inhalte enthält die Zustimmung zur sofortigen Erfüllung und den Verlust des Widerrufsrechts mit Beginn der Erfüllung. Der öffentliche Name ist Salomon Owona; der rechtliche Name steht nur in den Rechtstexten.

## Freigabe

Firmin hat am 12.11.2026 (t638u) den Go für den Live-Gang gegeben, nach Sichtung von Vorschau, Preisen und Rechtstext-Entwürfen. 205 bleibt gesperrt, bis ein EPUB mit dem englischen Titel vorliegt. 235/236 bleiben bis zum Lektorat gesperrt. Rechtstexte sind geprüfte Entwürfe.

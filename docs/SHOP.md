# Shop salomonowona.com

Stand: 12. November 2026. Der Shop liegt in diesem Branch, ist **nicht** auf Produktion freigeschaltet und verkauft nichts.

## Architektur

- **Frontend:** statisches HTML im bestehenden Repo, im Design der Website (dunkler Grund, Akzent `#d4a373`). Kein Vite, kein zweites Framework. Produktseiten sind echte Dateien mit schema.org (`Book` + `Product` + `Offer`), damit Suche und LLMs sie lesen können. `sitemap.xml`, `llms.txt` und `robots.txt` sind ergänzt.
- **Zahlung:** derselbe **om-api**-Stack wie der Shop auf owona.de (Stripe-Karte in EUR, NotchPay mit MTN/Orange Money in XAF, Kurs 655). Das Frontend spricht nach Freigabe `https://owona.de/api/…` mit `shop=salomonowona`. Die Erweiterung liegt in einem eigenen PR am Repo OwonaMedia/OM; sie ist nicht ausgerollt, und der Server-Schalter `SO_SHOP_ENABLED` bleibt aus (Standard `0`, keine Env-Änderung).
- **Erfüllung:** jeder kaufbare Titel ist fest an eine Archiv-ID gebunden (`ebook_id`). Der Server darf daraus kein neues Buch erzeugen. Lieferung per E-Mail-Download wie im OM-Shop, nur Deutsch.
- **Feature-Flag:** `shopLive: false` im Frontend (`shop/products.json`). Die Kasse simuliert nur einen Testkauf. Selbst wenn jemand das Frontend-Flag umlegt, lehnt die API ohne `SO_SHOP_ENABLED=1` ab (403).

## Katalog

Acht Kategorien: Herkunft & Migration, Musik & Beats, Liebe & Familie, E-Commerce, Krypto, Vibe Coding & KI, Geschichte & Rassismus, Afro-Mythologie.

- Eigene Dateien: 235, 236, 197–205. **Nicht** enthalten: OM-Shop 230–234, CSEB, zurückgezogenes 169, sensible 211/212.
- 197–204: lektorierte deutsche Fassungen, Shoppreis **4,99 €** (KDP-Metadaten nannten 2,99 €).
- 235 und 236: Manuskript fertig, **Lektorat ausstehend**, deshalb nicht kaufbar. Preisvorschlag 9,99 € (236 in den KDP-Daten 2,99 €).
- 205: Lektoratsfassung, aber Fließtext und Kapitelüberschriften sind englisch — nicht kaufbar, bis das geprüft ist.
- Afro-Mythologie bei Amazon (keine eigene Datei, Link zu Amazon): Horus (B0GSSFG63W), Ra (B0GSWT8YYT), Eshus Algorithmus (B0GHQ3L38Y), Ala (B0GTFPY8D3). Ein fünftes Listing war über die Kurzlinks nicht eindeutig zu bestätigen.

## Rechtstexte

AGB und Widerruf unter `/shop/agb` und `/shop/widerruf` sowie ein Abschnitt zu Stripe/NotchPay in der Datenschutzerklärung sind **Entwürfe – rechtliche Prüfung nötig**. Der Widerruf für digitale Inhalte enthält die Zustimmung zur sofortigen Erfüllung und den Verlust des Widerrufsrechts mit Beginn der Erfüllung. Der öffentliche Name ist Salomon Owona; der rechtliche Name steht nur in den Rechtstexten.

## Freigabe (noch nicht erteilt)

Vor dem Verkauf braucht es Firmins Go und: rechtliche Prüfung, Lektorat 235/236, Klärung 205, Preise, das fünfte Amazon-Titel, Ausrollen des OM-API-PR, `SO_SHOP_ENABLED=1` (Env, nur mit ausdrücklichem OK), CORS greift dann per Code für salomonowona.com, SKU-Zuordnung in der Shop-Bridge (Datenbank, nur mit OK), Stripe- und NotchPay-Webhooks bzw. Erfolgs-URLs für diese Marke, E-Mail-Absendertext.

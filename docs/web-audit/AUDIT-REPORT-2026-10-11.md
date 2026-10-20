# Audit-Kurzbericht — salomonowona.com (2026-10-11)

Vollständiger Durchgang nach `.cursor/plans/01-bug-ux-public-pruefung.plan.md` und `02-content-i18n-tiefenpruefung.plan.md`.

## Abdeckung

| Bereich | Status |
|---------|--------|
| Live `/`, `/en`, `/fr`, `/sw` | 200 OK (Vercel) |
| Assets `Salomon.png` | 200 |
| Assets `salo.png` | 404 Live — **nicht** im HTML referenziert |
| Sections home→contact | Parität in allen 4 Locales |
| Playlist 13 Tracks | Parität; einzelne Archive.org-URLs können 503 liefern |
| Externe Links (Beatstars, Patreon, TikTok, whatsapp.owona.de) | 200 |

## Bestätigt & korrigiert (lokal in allen 4 HTML-Dateien)

| Prio | Finding | Fix |
|------|---------|-----|
| P1 | Doppeltes `class` auf Lang-Buttons → `.active` wirkungslos; DE immer „aktiv“ | Ein `class="lang-btn active"` je Locale |
| P1 | Kein `hreflang` / `canonical` | Self-canonical + de/en/fr/sw + `x-default` |
| P1 | Apple-Podcasts-Placeholder `[dein-podcast]` | Link entfernt |
| P1 | Play-Button ohne Name/Zustand | `aria-label`, `aria-pressed`, ▶/❚❚-Toggle |
| P1 | Hamburger als `div` | `<button>` + `aria-expanded` / Escape schließt Menü |
| P1 | Radio-Fehler nur in Console | Sichtbare Meldung im Track-Titel (lokalisiert) |
| P1 | Titel beim ersten Play nicht gesetzt | `updateArchiveTitle()` beim Start |
| P2 | Beatstars ohne `rel` | `noopener noreferrer` |
| P2 | whatsapp.owona.de nur Text | echte Links |
| P2 | Kein Focus-/Motion-Schutz | `:focus-visible` + `prefers-reduced-motion` |
| P2 | Touch-Targets Play/Menü knapp | auf 32×32 px |

## Bewusst so belassen

- **Tailwind CDN** ohne SRI — würde CSP/`nonce` brauchen; P2 Follow-up.
- **Kein CSP-Header** — Inline-JS + CDN; Härten separat.
- **`Salomon.png` ~1.2 MB** — LCP-Thema; Kompression/WebP Follow-up, kein Redesign.
- **`salo.png` 404 Live** — ungenutzt im Markup; optional aus Deploy entfernen oder wieder einbinden.
- **Archive.org 503** bei einzelnen Tracks — Player skippt weiter; intermittierend serverseitig.
- **`automat.owona.de` 502** — außerhalb Scope.
- **Patreon-iframe** — lädt; sandboxen wäre Follow-up.

## Dateien geändert

- `index.html`, `en.html`, `fr.html`, `sw.html`

## Noch nicht live

Fixes sind lokal. Deploy auf Vercel nur auf Auftrag.

## Smoke nach Fix (lokal)

- JS-Syntax aller 4 Dateien: OK (`new Function`)
- Active-Locale korrekt: DE/EN/FR/SW
- Kein Podcast-Placeholder mehr
- hreflang-Cluster vollständig

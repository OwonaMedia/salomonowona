# CHANGELOG-agents – salomonowona-website

Protokoll der Änderungen von BoBo (Grok Bot) und seinen Agenten. Neueste zuerst, Zeiten Europe/Berlin. **Keine Secret-Werte** (nur Variablennamen).
Server-weite Änderungen (Ports, Supabase, SSH-Key, Cron, Rotation): siehe `~/Documents/Projects/_ops/SERVER-CHANGELOG.md`.
Vor Arbeit beide Dateien lesen; jede eigene Änderung hier nachtragen (Was/Warum/Wo/Backup/Freigabe/Status/PR).

---

## 2026-10-20
- **Offene Punkte aus GROKBOT/Audit geschlossen** (Auftrag: offene Ops-Quellen). Status: lokal umgesetzt, Deploy folgt per Push.
  - Impressum/Datenschutz (DE + EN/FR/SW), Footer-Links, Vercel-Rewrites.
  - SW-Bio: Ankunft DE **1989** (statt fälschlich 1981) in `index.html`/`sw.html`.
  - Doppelte/alte hreflang-Tags entfernt (kein `/sw` mehr im alternate-Block).
  - Hero: `Salomon.webp` (~58 KB) via `image-set`, PNG-Fallback.
  - Tailwind `@4.3.3` mit SRI; Security-Header inkl. pragmatischer CSP in `vercel.json`.
  - Radio Contabo: Tracks `07-king-dream.mp3` (IA MLKDream, Public Domain) + `10-traore-sovereignty.mp3` (IA WAWUNDI Ibrahim Traoré); Playlist 13/13; Liquidsoap restart.
- Freigabe: User-Auftrag „führe die offenen punkte durch“. Backup Radio: bestehende Media-Dateien unberührt, nur Additions.

## 2026-10-16
- **Regel `.cursor/rules/shared-prod-server.mdc` angelegt** (alwaysApply: Repo zuerst, prod_sync bei Hotfix, Docker nur 127.0.0.1, Deploy Preflight→Deploy→Smoke→Watch, keine Secrets). Status: erledigt (nicht committet).
- Server-weite Änderungen am selben Prod-Server (Ports, Supabase, SSH-Key, Cron): siehe SERVER-CHANGELOG.

# Shanti Travel — Rapport SEO Dashboard — Handoff Document

**Purpose of this doc:** everything needed to continue this project in Claude Code (or any new session) without re-explaining the architecture. Written for future-Claude, not for Karan.

**Owner:** Karan (solo SEO/web consultant), non-technical on server/Linux admin but fluent across the rest of the stack.
**Client:** Shanti Travel (shantitravel.com) — French multilingual travel agency, tailor-made Asia trips.

---

## 1. What this project is

A monthly SEO/marketing reporting dashboard for Shanti Travel. Single HTML file, deployed on Vercel, reading live from a published Google Sheet. No backend, no database — the Sheet **is** the database.

**Live URL:** https://shanti-report-analysis.vercel.app/
**Sheet ID:** `1_-FKu4Xb4OfG4JXe0VW8p8exhKsQ-INl0GtZO_259Y0`
**Deploy method:** GitHub repo → Vercel auto-deploy on push. Karan uploads the HTML file to GitHub manually; Vercel picks it up.

---

## 2. Architecture — read this before touching anything

### 2.1 The data flow
```
Google Sheet (one tab per data source, one row per month)
        ↓ (published to web: Fichier → Partager → Publier sur le web)
gviz API — https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet={tabName}
        ↓ (fetched client-side on page load, no server)
rapport-v3-final.html (single file, ~90KB, vanilla JS, no build step)
        ↓ (deployed as index.html or similar)
Vercel — static hosting only
```

**Critical:** the HTML file holds ZERO data. It is a pure reader. Data comes from two places — the Sheet (pasted via the Sidebar) and versioned JSON files in this repo under `data/` (see §2.2b). Updating the report = updating one of those two, NOT redeploying the HTML (redeploy only needed when the *code/template* changes).

### 2.2b Repo data files — `data/<tab>/<YYYY-MM>.json` (added Aug 2026)

A second data channel that lets Claude update the report **by git commit alone**, with no Sheet write, no Sidebar paste, and no Google auth.

```
data/
  index.json          ← manifest: {"ai": ["2026-07"], ...}  — which files exist
  ai/2026-07.json     ← merged OVER the Sheet's `ai` row for that month
```

- Served by Vercel from the **same origin** as `index.html`, so no CORS and no credentials.
- `loadAllData()` reads `data/index.json` first, then fetches only the files it declares — so there are no 404s in the console. If the manifest is missing, this whole step is skipped and the dashboard behaves exactly as before.
- Merge is **per top-level key, file wins**: a file containing only `{"gscAI": {...}}` adds that key and leaves `brandRadar`, `bing`, etc. from the Sheet untouched. This is why the file should contain *only* the keys Claude generates.
- Valid tabs: `vercel`, `gsc`, `ahrefs`, `keywords`, `ai`, `deep_analysis` (mapped to `STORE.kw` / `STORE.deep` for the last two).

**Never hand-edit `data/index.json`.** Write files with the helper, which rewrites the manifest for you:

```bash
node tools/write-data.js ai 2026-07 paste_AI_GSC_JUILLET.json
node tools/write-data.js --reindex     # manifest only
```

**Why this exists:** the GSC "Generative AI Features" report is not exposed by the GSC API (the `searchAppearance` dimension returns zero rows for it even when the UI shows ~150k impressions — verified Aug 2026), so it can only arrive as a manual CSV export. Rather than adding a monthly Sidebar paste, Claude converts the CSVs and commits the result here. Automating the *Sheet* side instead was attempted and abandoned: `clasp run` needs the Apps Script API + an OAuth consent that Google blocks for clasp's public client ("This app is blocked"), and the alternative — a public `doPost` web app — was rejected as it means an internet-reachable endpoint that can write to the Sheet.

### 2.2 Sheet tabs (each is `month | label | json` except `shared` and `ga4`/`ga4_channels`)

| Tab | Format | Populated by | Notes |
|---|---|---|---|
| `index` | `month \| label` | Manual + Apps Script | Master list of which months exist. Must be `2026-04` format, NOT `2025-04` or a Date object — see §4.1 |
| `vercel` | `month \| label \| json` | Manual paste via Sidebar | Vercel Analytics export → JSON |
| `gsc` | `month \| label \| json` | Manual paste via Sidebar | Google Search Console via MCP |
| `ahrefs` | `month \| label \| json` | Manual paste via Sidebar | Ahrefs via MCP |
| `keywords` | `month \| label \| json` | Manual paste via Sidebar | Ahrefs top keywords via MCP |
| `ai` | `month \| label \| json` | Manual paste via Sidebar | SERP features + Brand Radar + Bing citations, all merged into one JSON |
| `deep_analysis` | `month \| label \| json` | Manual paste via Sidebar | GSC × Ahrefs cross-analysis, optional monthly |
| `shared` | single row, `json` only | Manual paste via Sidebar | Competitors + backlinks, rarely changes |
| `ga4` | raw Coupler.io rows (NOT the month\|label\|json pattern) | **Automatic** via Coupler.io | Landing page performance. Coupler writes raw tabular rows; a dedicated `fetchGA4()` JS function groups them by month using a `Dimension: Report month` column |
| `ga4_channels` | raw Coupler.io rows | **Automatic** via Coupler.io | Traffic by channel. Same raw-row pattern, dedicated `fetchGA4Channels()` |

### 2.3 Dashboard tabs (in the UI, defined in the `PAGES` array in the JS)
```
Vue d'ensemble → Trafic Vercel → Performance GSC → Ahrefs SEO → Backlinks & Concurrents
→ Mots-clés Ahrefs → Analyse Approfondie → Visibilité IA → Visibilité IA 2 → Google Analytics 4
```

- **Visibilité IA** — month-driven, reads from the `ai` sheet tab
- **Visibilité IA 2** — ⚠️ **STATIC, NOT month-driven.** Data is hardcoded directly into the HTML as a JS constant (`AI2_DATA`), not read from the Sheet. It shows the same one-off snapshot (540 AI citation tests from a July 1 2026 Ahrefs export) regardless of which month is selected in the dashboard. If this needs updating, it requires editing the HTML directly, not pasting into the Sidebar.

### 2.4 Key JS internals (for when you need to edit the HTML)
- `SHEET_ID` — const at top of the `<script>` block
- `fetchTab(tabName)` — raw gviz fetch for one tab
- `fetchTabRows(tabName)` — parses the `month | label | json` pattern into `{month: {...parsedJSON}}`
- `gvizToMonthKey(v)` — **critical helper.** Google Sheets auto-converts `2026-05`-style strings into Date objects; gviz then returns them as `Date(2026,4,1)` strings (month is 0-indexed!). This function normalizes any of: clean `YYYY-MM` string / gviz `Date(...)` string / JS Date-toString string → clean `YYYY-MM`. Used everywhere a month key is read (index tab, all data tabs, ga4 tabs). **If you ever see data "not loading" for a specific month, suspect this first** — check if the raw sheet cell became a Date-formatted cell instead of plain text.
- `fetchShared()` — reads the single-row `shared` tab, handles Google Sheets' quote-escaping of JSON-in-cell (`""` → `"`)
- `fetchGA4()` / `fetchGA4Channels()` — read Coupler.io's raw row format, group by month via `gvizToMonthKey` on the `Dimension: Report month` / `Report: Month` column
- `loadAllData()` — fires all `fetchTabRows`/`fetchGA4`/`fetchShared` calls in parallel, populates global `STORE`
- `loadMonth(key)` / `assembleMonth(key)` — assembles one month's full data object from `STORE`, **must explicitly copy every field** (this bit us once — `deep` and `ga4`/`ga4ch` were forgotten in `assembleMonth` and silently showed "no data" for weeks; if you add a new data source, check BOTH `loadMonth` and `assembleMonth`)
- `secOverview`, `secVercel`, `secGSC`, `secAhrefs`, `secLinks`, `secKw`, `secDeep`, `secAI`, `secAI2`, `secGA4` — one render function per dashboard tab, each takes the assembled month object and returns an HTML string
- Every `secXxx` function **must null-guard** at the top (`if(!x||!x.kpi) return noData(...)`) — sheet tabs are often empty for a given month and the renderer must degrade gracefully, not throw

### 2.5 Known JSON quirk
When Google Sheets stores a large JSON blob typed/pasted into a cell, it sometimes wraps it in outer double-quotes with `""` escaping (classic CSV-style escaping) instead of a clean JSON string. `fetchTabRows` and `fetchShared` both try `JSON.parse()` directly first, and on failure strip outer quotes + unescape `""` → `"` before retrying. If a paste ever fails to load, this is the second thing to suspect (after the date/month-key issue above).

---

## 3. The Apps Script side (Sidebar + Code.gs)

Bound to the Google Sheet. Two files: `Code.gs` (backend logic) and `Sidebar.html` (the paste UI).

- Menu: **📊 Rapport SEO** → Ouvrir le panneau / Initialiser les onglets / 🧹 Nettoyer les doublons index / 🔧 Corriger toutes les clés de mois
- `DATA_TABS` const lists every `month|label|json` tab — extend this when adding a new tab
- `upsertRow(tab, monthKey, label, jsonStr)` — the core save function, finds existing row for that month key and overwrites, or appends new
- `syncIndex(monthKey, label)` — keeps the `index` tab in sync, avoids duplicate rows (this had bugs early on — see §4.1)
- `saveVercel`, `saveGSC`, `saveAhrefs`, `saveKeywords`, `saveAI`, `saveDeepAnalysis`, `saveShared` — one function per tab, all wrap `validateAndSave`
- `updateDeepAnalysisStatus(monthKey, section, query, newStatus)` — lightweight status updates (open/in_progress/fixed) inside the deep_analysis JSON without re-pasting the whole blob
- `fixAllMonthKeys()` / `deduplicateIndex()` — one-time cleanup utilities, safe to re-run, normalize messy date-typed cells back to `YYYY-MM` strings and remove duplicate index rows

Sidebar sections (in order): Vercel → GSC → Ahrefs → Visibilité IA (+ Bing hint) → Mots-clés → Analyse Approfondie (+ status-update mini-form) → Analyse (free text, optional, unused so far) → Concurrents/Shared.

---

## 4. War stories — bugs already fixed, don't reintroduce them

### 4.1 Date-typed month keys (the recurring root cause)
Google Sheets silently converts a typed `2026-05` into an actual Date cell. This broke almost everything at least three separate times across this project:
- Index tab showing duplicate months (`2025-04` AND `2026-04` both existing)
- Deep Analysis tab showing "no data" despite data being present (key was `Date(2026,4,1)`, lookup was for `"2026-05"`)
- GA4 tabs same issue with a different column name (`Dimension: Report month`)

**Fix pattern:** always run data through `gvizToMonthKey()` before using it as an object key, on both the JS side and conceptually on the Apps Script side (`fixAllMonthKeys()`).

### 4.2 `assembleMonth` / `loadMonth` silently dropping fields
Twice now, a new data source (`deep`, later `ga4`) was wired into `STORE` and `loadMonth` correctly, but forgotten in `assembleMonth`'s return object — result: the section always rendered the "noData" fallback even though the data was present in memory (confirmed via console: `STORE.deep` had it, `d.deep` inside the renderer was `undefined`). **When adding a new data source, grep for every place `d.xxx` needs to appear and check all of: `STORE`, `loadMonth`, `assembleMonth`.**

### 4.3 `movers` array vs object format mismatch
The Ahrefs "gains/pertes" tables expect `movers.up`/`movers.down` as arrays-of-arrays `[kw, vol, prev, cur]`, matching how the original May data was shaped. A later month's JSON used objects `{kw, vol, prev, cur, d}` instead → rendered as `undefined`/`NaN` everywhere. Similarly `buckets` expects `{top3, mid, low}` — Ahrefs' native field names are `{top3, top4_10, top11_20, top21_50, top51_plus}` and need remapping before pasting (or `stackedBuckets()` needs to accept both, which it now does defensively).

### 4.4 Setup regressions from refactors
At one point a full duplicate helper block (`fmt`, `esc`, `delta`, `kpiCard`, etc.) got left in from a v2→v3 merge, and separately the entire `loadAllData`/`loadMonth`/`STORE`/`MONTHS` block was missing entirely after an edit (page was totally broken, `setStatus is not defined`). **Always run a Node syntax check (`node --check`) after any HTML edit, and ideally a headless smoke-test (eval the script, mock `document`/`fetch`, call a render function directly, check output length/contains) before telling Karan to redeploy** — this caught several otherwise-invisible breakages in this project.

---

## 5. Monthly workflow (what actually happens every month)

1. Karan says "pull GSC + Ahrefs [month]" or similar
2. Claude pulls GSC via MCP (`get_advanced_search_analytics` — query/page/country dimensions, 50/50/20 row limits) and Ahrefs via MCP (`site-explorer-metrics-history`, `site-explorer-backlinks-stats`, `site-explorer-domain-rating-history`, `site-explorer-keywords-history`, `site-explorer-organic-keywords` with `date_compared` for movers)
3. Claude builds the JSON matching each tab's expected shape (see actual example files, listed below) and gives Karan a downloadable file
4. Karan pastes Vercel CSVs (4 files: Top Countries / Top Devices / Top Referrers / Top Pages) — Claude converts to JSON
5. Karan pastes all JSONs into the Sidebar, one per section, with the month key/label
6. GA4 is the exception: Karan just clicks "Run" on two Coupler.io dataflows (Landing Page performance → `ga4` tab, Monthly sources performance → `ga4_channels` tab) — fully automatic, no JSON round-trip
7. AI visibility: Ahrefs SERP overview (per-keyword, ~9 tracked keywords) + Brand Radar screenshot numbers (Karan reads from Ahrefs UI, since the Brand Radar API needs a paid add-on we don't have) + Bing Webmaster Tools export (2 CSVs: AI Page Stats + AI Search Queries) — all three merged into one `ai` JSON

**No Vercel redeploy is needed for a normal monthly update** — only when the HTML template itself changes.

---

## 6. Known limitations / things not solved

- **Ahrefs Brand Radar API** requires a paid add-on ($398–699/mo) not on the current Standard plan — confirmed via direct API test (`"Missing addon: Brand Radar"`). Brand Radar numbers are manually transcribed from the Ahrefs UI screenshot each month, not pulled via API.
- **Ahrefs Web Analytics script** is NOT installed on shantitravel.com, so no direct LLM-referral traffic tracking from Ahrefs. Real LLM referral traffic (ChatGPT, Perplexity, Gemini, Copilot) is instead read from Vercel's referrer breakdown and manually added to the `ai.llmReferral` field.
- **GSC's URL Inspection API does not expose hreflang data** — confirmed by testing. Only canonical/indexing/rich-results. Any hreflang debugging must be done via raw page-source (`view-source:`) inspection, not GSC API.
- **GSC only retains ~16 months of data** — year-over-year comparisons need proactive backfilling into the Sheet before the data ages out, or it's lost permanently.
- **Visibilité IA 2 is static** (see §2.3) — needs manual HTML edit to refresh, not sidebar-driven.

---

## 7. Outstanding / recently discussed but not built

- **Phase 2 recommendations** (from a deep two-phase analysis of a colleague's GSC decline report) — a prioritized list of dashboard additions: YoY comparison columns + backfilling 2025 data before it ages out of GSC (top priority), a demand/search-volume index per destination, brand-vs-nonbrand trend line, CTR-at-stable-position tracker (proxy for AI Overview erosion), commercial-vs-informational query split, a "GEO funnel" (bot crawls → AI citations → AI referral visits → GA4 conversions), SERP feature ownership count, conversions-per-landing-page via GA4 key events, an indexation health panel. None of this is built yet — see conversation history for full detail if resuming this thread.
- **hreflang bug investigation** — confirmed (via live page-source comparisons + a 144-row Ahrefs Site Audit export) that the site's hreflang failure is a **template-level bug**, isolated to guide pages (72% of all errors) and program pages (15%), NOT a Strapi content-linking issue as a colleague (Sébastien) initially theorized. Destination pages render hreflang correctly; guide/program pages don't, even when Strapi locales are correctly linked. This is now a developer ticket, not a content/CMS task. Full technical reasoning and the falsification tests are in conversation history if needed again.
- **A separate `og:locale:alternate` duplication bug** was spotted on the homepage (French listed twice) — flagged but not yet investigated further.

---

## 8. File inventory (what's in /mnt/user-data/outputs/ as of this handoff)

**Core files (always current, these are what matter going forward):**
- `rapport-v3-final.html` — the live dashboard source, push this to GitHub to deploy
- `Code.gs` — Apps Script backend
- `Sidebar.html` — Apps Script paste UI
- `FixSheet.gs` — one-time cleanup utility (date/duplicate fixes), safe to keep as a menu item

**Reference/example JSON payloads (one per tab per month, useful as shape-reference for future months, NOT meant to be re-pasted as-is):**
`paste_AHREFS_*.json`, `paste_GSC_*.json`, `paste_KW_*.json`, `paste_VERCEL_*.json`, `paste_AI_*.json`, `paste_BING_JUILLET.json`, `paste_DEEP_ANALYSIS_2026-06.json`, `paste_SHARED.json`, `paste_AI_GAP_REPORT.json` (source data for the static Visibilité IA 2 tab)

**Old/superseded, safe to ignore or delete:**
`rapport-seo-shantitravel.html` (v1), `rapport-seo-template.html`, `rapport-v2-sheet-driven.html` — earlier iterations kept only for UI/CSS reference, not in use.

**Docs already written:**
`GUIDE_INSTALLATION.md`, `MONTHLY_UPDATE_PROMPT.md`, `VERCEL_TO_JSON_PROMPT.md`, `D-schema.md` — pre-existing docs, may be partially stale versus this handoff doc; this HANDOFF.md supersedes them for architecture questions.

---

## 9. Transferring this to Claude Code

**Files:** yes, manual transfer is the only way — there's no direct bridge between claude.ai and a local Claude Code project folder. Two practical options:

1. **Download + move**: Karan downloads every file from this conversation's outputs (already offered via the file cards throughout), drops them into a local project folder, then opens that folder in Claude Code (`claude` in the terminal, or the desktop app's Code tab). This is the simplest path — small file count (~35 files, mostly small JSON), no repo needed yet.
2. **Via the existing GitHub repo**: since the HTML is already pushed to a GitHub repo for Vercel deployment, Karan can `git clone` that repo locally and open it in Claude Code directly — this also gives proper version history going forward, which the current manual-download workflow doesn't have. This is the better long-term choice if the repo isn't already cloned locally.

Either way, **this HANDOFF.md should go in the project root** so a fresh Claude Code session (with no memory of this conversation) can read it first and get full context immediately — that's the entire purpose of this document.

**Recommended first message to Claude Code once set up:** *"Read HANDOFF.md before doing anything else."*

# GA4 Deep Dive — Handoff

**Status:** analysis complete, **not yet integrated** into the dashboard. Nothing committed.
**Date:** 1 September 2026
**Read with:** root `HANDOFF.md` (§2.2b repo data channel, §5 monthly workflow, §7 outstanding) and `D-schema.md`.

---

## 1. What this is and why it exists

A direct GA4 Data API pull for `www.shantitravel.com`, covering **Apr–Aug 2026 with Apr–Aug 2025 as year-on-year comparison**. It produces a management-facing performance report plus a technical annex on data quality.

It exists because the dashboard's current GA4 page (`secGA4`, fed by the two Coupler.io dataflows into the `ga4` / `ga4_channels` Sheet tabs) shows single-month channel and KPI data only. It has no year-on-year columns, no landing-page conversion data, and no funnel view.

Root `HANDOFF.md` §7 lists three of these as outstanding and unbuilt:

- *"YoY comparison columns + backfilling 2025 data before it ages out"* — **delivered here** for GA4 (GSC backfill is still open, separate problem)
- *"conversions-per-landing-page via GA4 key events"* — **delivered here**
- *"GEO funnel (bot crawls → AI citations → AI referral visits → GA4 conversions)"* — the last leg is delivered here; AI Assistant channel sessions and their conversions are broken out

This does **not** replace the Coupler.io GA4 feed. That stays as-is and remains fully automatic.

---

## 2. Files

All in `ga4-report/`. Nothing outside that folder was touched.

| File | What it is |
|---|---|
| `ga4-performance-report-apr-aug-2026.md` | **The report.** Management-facing. YoY + MoM throughout. Start here. |
| `ga4-data-quality-annex.md` | Technical annex — the tracking problems, in detail. Referenced from the report's §8. |
| `ga4-deep-dive.json` | **Curated, structured output — this is the integration candidate.** 31 KB. |
| `ga4-raw.json` | Every raw API response, 33 sections. 504 KB. Reference only, do not ship to the dashboard. |
| `ga.py` | Minimal GA4 Data API client. Reads the key path from `GA4_KEY`, never logs it. |
| `pull.py` | Section A–N pull, Apr–Aug 2026 |
| `pull2.py` | Conversion-window pull, Jul–Aug 2026 |
| `pull3.py` | Year-on-year pull, Apr–Aug 2025 |
| `build.py` | Assembles `ga4-deep-dive.json` from `ga4-raw.json` |

**Credentials.** Service account `ga4-reader@onyx-oxygen-506610-b4.iam.gserviceaccount.com`, read-only on GA4 property `352360511`. The key is *not* in this repo and must never be. It currently sits in `~/Downloads` and should be moved somewhere private and rotated — its contents were pasted into a chat session.

**Dependencies:** none to install. Uses `google-auth` and `requests`, both already present. No BigQuery involved.

**To re-run:**

```bash
cd ga4-report && export GA4_KEY="/path/to/key.json" && python pull.py && python pull2.py && python pull3.py && python build.py
```

---

## 3. Findings, in one line each

Full detail in the two `.md` files — not repeated here.

- Sessions **−45% YoY**; 87% of the loss is Paid Search (−54%) and Organic Search (−45%)
- Inquiry volume is **flat** despite that, so the inquiry rate roughly **doubled** (3.6% → 6.8%)
- Destination pages are **growing** (Philippines +170%, Sri Lanka +88%); the homepage is −36%
- Mobile engagement fell **11 points** YoY while desktop was flat — mobile is 71% of traffic
- **366 people in two months** completed the entire 7-step inquiry form and did not submit
- Three tracking defects make raw GA4 conversion counts unusable — see the annex

---

## 4. Integrating into the dashboard

### 4.1 The two structural problems

**(a) The `ga4` page cannot be fed from repo files.** `index.html` builds `STORE.ga4` / `STORE.ga4ch` from `fetchGA4()` / `fetchGA4Channels()`, which read the Sheet. The repo-file channel's `storeKeys` map (`index.html` ~line 381) covers only `vercel, gsc, ahrefs, keywords, ai, deep_analysis` — `ga4` is not in it. So this data cannot land on the existing GA4 page without a code change either way.

**(b) The dashboard is month-keyed; this report is period-keyed.** Every repo data file is `data/<tab>/<YYYY-MM>.json` and the UI assembles one month and compares it to the previous one. `ga4-deep-dive.json` covers a 5-month block with a 12-month-offset comparison. It does not fit the existing shape as-is.

This is the decision that has to be made before any code is written. Options in 4.3.

### 4.2 Recommended route — a new `ga4_deep` tab

Cleanest separation, leaves the Coupler-fed GA4 page untouched. Three small edits:

1. **`tools/write-data.js`** — add `'ga4_deep'` to the `TABS` array (line ~15). This is also what makes `--reindex` pick the folder up.
2. **`index.html` ~line 381** — add `ga4_deep:'ga4deep'` to the `storeKeys` map.
3. **`index.html` ~line 1230** — add a `PAGES` entry, e.g. `{id:"ga4deep", label:"GA4 Analyse", fn:(d,prev)=>secGA4Deep(d,prev)}`, and write `secGA4Deep`.

Then:

```bash
node tools/write-data.js ga4_deep 2026-08 ga4-report/<reshaped>.json
```

**Never hand-edit `data/index.json`** — the helper rewrites it. (Root `HANDOFF.md` §2.2b.)

### 4.3 The month-key question — needs a decision

| Option | How | Trade-off |
|---|---|---|
| **A. Single period block under `2026-08`** | One file, whole Apr–Aug analysis, rendered as a standalone report page | Simplest. Doesn't participate in month switching — the page shows the same thing whichever month is selected, which will confuse people |
| **B. Split into five monthly files** | `2026-04` … `2026-08`, each with that month's traffic + YoY vs the same month 2025 | Fits the dashboard model properly, month switching works. But conversion data only exists for Jul/Aug, so three of five months render partly empty |
| **C. Both** | Monthly files for the trend metrics, one period block for the funnel and YoY summary | Most useful, most work |

**My recommendation is B**, with the conversion sections rendering the existing `noData()` helper for Apr–Jun. That's consistent with how the dashboard already handles missing months elsewhere, and it means the tracking gap is visible rather than hidden.

### 4.4 Schema work still to do

`ga4-deep-dive.json` was shaped for readability, not for this dashboard. It does **not** follow `D-schema.md` conventions. Before integration someone needs to reshape it to match, and add the result to `D-schema.md` as a new section. Its current top-level keys:

```
meta · basic_metrics · monthly_www · channels · devices · inquiry_funnel
landing_pages · mobile_desktop_gaps · ai_traffic · geography · languages
content_trend · data_quality_issues
```

`meta` deliberately carries `conversion_window`, `key_event_inflation_factor: 2.0` and the reason for each, so any consumer can avoid reporting the inflated numbers. **Whatever shape it is reshaped into must keep those fields** — they are the guard against someone quoting a 2× conversion count.

### 4.5 Two conventions this respects

- **Never truncate to a top-N** (root `HANDOFF.md` §5.3). Landing pages are capped at 40 in the curated file for weight; the full list is in `ga4-raw.json` and the cap should be lifted or raised when reshaping.
- **Merge is per top-level key, file wins.** A `ga4_deep` file only ever adds its own keys; nothing else in the store is affected.

---

## 5. Open questions

1. **Month-key model** — A, B or C from §4.3. Blocks everything else.
2. **Ad spend.** Not available for this report, so there is no cost-per-lead anywhere. Monthly spend per channel would make §3 of the report far more useful and is normally the most-read table.
3. **Refresh cadence.** GA4 is currently the one source needing no monthly Claude involvement (root `HANDOFF.md` §5.5). Adding this changes that — the scripts are re-runnable but someone has to run them. Monthly, quarterly, or on request?
4. **Should the tracking defects be fixed first?** Three of them (double-counted key events, guest forms counted as leads, tracking absent before July 2026) are GA4 configuration problems, not dashboard problems. Fixing them makes every future report cleaner and cheaper. Detail in the annex.

---

## 6. What was deliberately not done

- No git commit, no push, no branch
- No changes to `index.html`, `tools/write-data.js`, `data/`, or any existing file
- No files written to `data/` — the reshaping decision in §4.3 comes first
- BigQuery — explicitly deferred to a later step
- GSC Bulk Data Export — still not enabled. Worth noting it does **not backfill**, so every day it stays off is a day of search data that cannot be recovered later.

# Shanti Travel — GA4 Deep Dive

Property `352360511` · pulled via GA4 Data API on 2026-09-01

**Two windows, and they are not interchangeable:**

- **Traffic & engagement:** 1 Apr – 31 Aug 2026 (5 months)
- **Conversions:** 1 Jul – 31 Aug 2026 (2 months) — conversion events did not exist on `www` before July

---

## 0. Read this before trusting any conversion number

### 0.1 Conversion tracking on the main site started in July 2026

| Month | www sessions | key events |
|---|---:|---:|
| Apr 2026 | 11,455 | **0** |
| May 2026 | 10,227 | **0** |
| Jun 2026 | 9,774 | **0** |
| Jul 2026 | 10,807 | 401 |
| Aug 2026 | 11,280 | 1,032 |

April–June conversion data does not exist. Any report that averages Apr–Aug conversions is wrong by roughly 60%. The jump from 401 to 1,032 is tag rollout, not growth.

### 0.2 Every lead is counted twice

On `www`, two events fire per inquiry and **both are marked as key events**:

| Event | Events | Users |
|---|---:|---:|
| `inquiry_submitted` | 735 | 696 |
| `demande_voyage_fr` | 706 | 668 |

Near-identical user counts. These are the same lead tagged twice.

**Reported: 1,433 key events. Actual leads: ~700.**

### 0.3 Two different businesses are being added together

`connect.shantitravel.com` is existing-guest servicing (pre/post-trip forms, reviews). Its submissions are counted as key events alongside sales leads.

| Domain | Sessions | Key events | What it actually is |
|---|---:|---:|---|
| `www.shantitravel.com` | 51,678 | 1,433 | New business |
| `connect.shantitravel.com` | 15,369 | 2,652 | Existing guests |
| **Property total** | 65,090 | **4,085** | Meaningless as one number |

**65% of the property's "conversions" are not leads.** They're guests filling in trip forms. And on `connect` the same double-count applies (`Tally.FormSubmitted` 1,332 + `demande_voyage_fr` 1,294 = ~1,330 real submissions).

So the honest headline: **~700 sales leads and ~1,330 guest submissions in the period** — not 4,085 conversions.

### 0.4 Smaller issues

| Issue | Detail |
|---|---|
| Junk traffic | 826 Jul–Aug sessions with landing page `(not set)`, 4% engagement, 96% bounce. Plus 3,015 Apr–Aug sessions with `newVsReturning` unset at 0.4% engagement. |
| Dev traffic in production | `localhost`, seven Vercel preview URLs, `translate.goog` (~90 sessions) |
| Cross-domain leak | `connect` starts its own sessions: 1,743 as `(direct)`, 941 as `(not set)` — real acquisition channels lose the credit |
| Perplexity misclassified | Lands in `Unassigned`, not GA4's native `AI Assistant` channel |

---

## 1. Basic metrics (www, Apr–Aug 2026)

| Metric | Value |
|---|---:|
| Sessions | 51,678 |
| Users | 42,414 |
| New users | 41,083 (**96.9%**) |
| Engagement rate | 65.4% |
| Avg session duration | 3m 03s |
| Pages per session | 2.35 |
| Reported key events | 1,433 |
| **Estimated real leads** | **~716** |

Monthly sessions: 11,455 → 10,227 → 9,774 → 10,807 → 11,280. Flat with a June dip. No trend to worry about.

**96.9% new users is the outlier here.** For a considered purchase like a multi-week trip to Asia, almost nobody returning is unusual. Either the remarketing/return path is broken, or people research once and convert elsewhere (phone, email). Worth understanding — it's the difference between a leaky funnel and a single-visit sales model.

`connect` for contrast: 15,369 sessions, 38.1% engagement, 1.04 pages/session, 99s. People land, submit, leave. That's a form, working as intended.

---

## 2. The inquiry funnel — the biggest single finding

You have a 7-step inquiry form instrumented with `step_id` / `step_index`. Almost nobody has this data. Here it is (users, Jul–Aug):

| Step | Users | Drop | % of entrants |
|---|---:|---:|---:|
| destinations | 1,414 | — | 100% |
| travelers | 1,322 | −6.5% | 93% |
| dates | 1,308 | −1.1% | 93% |
| budget | 1,280 | −2.1% | 91% |
| stage | 1,221 | −4.6% | 86% |
| story | 1,193 | −2.3% | 84% |
| contact | 1,062 | −11.0% | 75% |
| **submitted** | **696** | **−34.5%** | **49%** |

The form itself is excellent. Steps 1–6 lose only 16% combined — people happily give you destinations, dates, budget, and their travel story.

**Then a third of them walk away at the final step.**

366 people in two months filled in everything and did not submit. That is more than half of your actual lead volume, lost at the last click. Nothing else in this property is worth this much.

Two candidate causes, both testable: the contact step asks for something people won't give (phone number is the usual culprit), or it's failing on mobile. Section 4 makes the second look likely.

---

## 3. Channels (Jul–Aug, CVR de-duplicated)

| Channel | Sessions | Eng. rate | Avg dur | Pages/sess | Real CVR |
|---|---:|---:|---:|---:|---:|
| Paid Search | 7,725 | 73.5% | 161s | 2.34 | 3.84% |
| Organic Search | 7,059 | 61.3% | 232s | 2.49 | **1.49%** |
| Cross-network | 3,503 | 61.0% | 147s | 2.30 | 2.90% |
| Paid Social | 1,117 | 66.1% | 136s | 2.05 | **7.43%** |
| Unassigned | 1,077 | 72.4% | 209s | 1.99 | 4.18% |
| Direct | 1,013 | 65.3% | 268s | 2.96 | 6.22% |
| Referral | 305 | 73.8% | 254s | 2.34 | 2.46% |
| Email | 267 | 71.2% | 267s | 3.59 | 0.37% |
| Organic Social | 165 | 78.8% | 186s | 3.16 | 4.24% |
| AI Assistant | 118 | 68.6% | 245s | 2.87 | 2.54% |

**Organic search is the problem.** Near-identical volume to paid search (7,059 vs 7,725), converts at **39% of the rate**. Organic visitors stay *longer* (232s vs 161s) and read *more* (2.49 vs 2.34 pages) — they are engaged and they don't convert.

That is not a traffic problem. It's a mismatch between what organic visitors came for and what the page asks them to do. Paid traffic lands on pages built to convert; organic lands on guides and destination pages that inform and then stop.

**Paid Social converts nearly 2× paid search** at a tenth of the volume. Underspent.

**Email is broken:** 267 sessions, 71% engagement, 3.59 pages/session — the best content consumption on the site — and 2 conversions. Something is wrong at the end of that journey.

**Unassigned is 1,077 sessions (5%)** with above-average engagement. That's untagged campaign traffic you can't attribute.

---

## 4. Mobile is 71% of your traffic and it is failing

| Device | Sessions | Share | Eng. rate | Real CVR |
|---|---:|---:|---:|---:|
| Mobile | 15,413 | 70.6% | 64.4% | 3.01% |
| Desktop | 5,984 | 27.4% | **75.9%** | **3.95%** |
| Tablet | 661 | 3.0% | 68.8% | 2.42% |

Site-wide, mobile converts 24% worse. Per page, it's far uglier:

| Landing page | Mob. sess | Mob. CVR | Desk. sess | Desk. CVR | Gap |
|---|---:|---:|---:|---:|---:|
| `/fr/voyage-inde` | 548 | 1.8% | 135 | 8.5% | **+6.7pp** |
| `/fr/voyage-bali` | 729 | 2.4% | 109 | 8.7% | **+6.3pp** |
| `/fr/voyage-philippines` | 766 | 3.4% | 158 | 6.9% | +3.5pp |
| `/fr/voyage-ouzbekistan` | 170 | 2.4% | 51 | 5.9% | +3.5pp |
| `/fr/voyage-bhoutan` | 251 | 1.6% | 61 | 4.9% | +3.3pp |
| `/en` | 105 | **0.0%** | 155 | 3.2% | +3.2pp |
| `/fr/voyage-sri-lanka` | 1,154 | 2.8% | 218 | 5.9% | +3.1pp |

`/fr/voyage-inde` and `/fr/voyage-bali` convert **4–5× better on desktop**. These are top-traffic pages carrying 1,277 mobile sessions between them. Engagement on mobile is also 20+ points lower on both (63% vs 89%, 62% vs 86%).

This is very likely the same problem as the funnel's final-step collapse. Worth checking on a real phone before anything else.

`/en` converts **zero** on mobile across 105 sessions.

---

## 5. Content

**Top landing pages (Jul–Aug, real CVR):**

| Page | Sessions | Eng. | Bounce | Real CVR |
|---|---:|---:|---:|---:|
| `/fr/voyage-japon` | 1,698 | 71% | 29% | 3.33% |
| `/fr` | 1,455 | 87% | 13% | 3.64% |
| `/fr/voyage-sri-lanka` | 1,445 | 66% | 34% | 3.18% |
| `/fr/voyage-philippines` | 940 | 76% | 24% | 4.04% |
| `/fr/voyage-bali` | 885 | 65% | 35% | 3.16% |
| `/fr/voyage-inde` | 716 | 68% | 32% | 3.00% |
| `/fr/voyage-coree-du-sud` | 465 | 77% | 23% | 4.73% |
| `/fr/voyage-indonesie` | 385 | 74% | 26% | 4.42% |
| **`/fr/trips`** | **168** | **92%** | **8%** | **8.63%** |
| `/fr/departs-garantis-petit-groupe` | 175 | **90%** | **10%** | **0.00%** |

Two pages stand out at the bottom:

- **`/fr/trips`** converts at 8.6% — **2.4× the site average** — on 168 sessions. 92% engagement, 8% bounce. This is your best page and almost nobody sees it. It should be linked from every destination page.
- **`/fr/departs-garantis-petit-groupe`** has the best engagement on the site (90%, 10% bounce) and **zero conversions** in two months. People love it and there is no way to act on it. Cheapest fix on this list.

**Trend, Apr 1–Jun 15 vs Jun 16–Aug 31:**

| Gaining | | Losing | |
|---|---:|---|---:|
| `/fr/voyage-sri-lanka` | +108% | `/fr/voyage-bhoutan` | −54% |
| `/fr` | +61% | `/fr/trek-himalaya-indien` | −48% |
| `/fr/voyage-malaisie` | +52% | `/fr/guide-voyage-thailande/animaux-thailande` | −44% |
| `/fr/voyage-japon` | +46% | `/fr/voyage-taiwan` | −26% |
| `/fr/voyage-coree-du-sud` | +42% | `/fr/voyage-vietnam` | −21% |
| `/fr/voyage-ouzbekistan` | +38% | `/fr/voyage-chine` | −14% |

Note: `/fr/` (trailing slash) went 416 → 0. That's a URL change, not lost traffic — excluded above.

Bhoutan lost 54% of sessions but engagement *rose* from 41% to 70%. It shed low-quality traffic, which is fine. The others are worth a look in Search Console.

---

## 6. AI traffic (Jul–Aug)

| Source | GA4 channel | Sessions | Eng. | Avg dur | Pages/sess | Key events |
|---|---|---:|---:|---:|---:|---:|
| `chatgpt.com` | AI Assistant | 107 | 69.2% | 251s | **3.01** | 6 |
| `copilot.com` | AI Assistant | 6 | 66.7% | 279s | 1.83 | 0 |
| `perplexity` | **Unassigned** | 6 | 33.3% | 30s | 0.67 | 0 |
| `copilot.com` | **Unassigned** | 3 | 33.3% | 41s | 1.00 | 0 |
| `gemini.google.com` | AI Assistant | 3 | 100% | 134s | 1.67 | 0 |
| `perplexity.ai` | AI Assistant | 2 | 0% | 0s | 0.50 | 0 |

~127 sessions, **0.6% of traffic**. Small.

But ChatGPT visitors read **3.01 pages per session** against a site average of 2.35, and stay 251s against 183s. **The deepest-reading traffic on the site.** Low volume, high intent.

Caveats: 8 Perplexity/Copilot sessions land in `Unassigned` because GA4's native channel doesn't recognise Perplexity. And the referrer-less AI traffic — reportedly 35–70% of AI clicks — is invisible here and sitting inside Direct. So 127 is a floor, not a count.

---

## 7. Geography & language (Jul–Aug)

| Country | Sessions | Eng. | Real CVR |
|---|---:|---:|---:|
| France | 36,062 | 65.5% | 1.53% |
| Belgium | 3,942 | 68.9% | 2.04% |
| Switzerland | 2,071 | 69.2% | 0.82% |
| Germany | 1,812 | 56.5% | **0.22%** |
| India | 1,253 | 62.1% | **0.08%** |
| Indonesia | 934 | 58.0% | 0.70% |
| Canada | 699 | 63.4% | 1.00% |
| Sri Lanka | 326 | 56.1% | **0.00%** |

| Language | Sessions | Eng. | Real CVR |
|---|---:|---:|---:|
| French | 43,360 | 65.8% | 1.54% |
| English | 5,302 | 63.5% | **0.66%** |
| German | 2,670 | 56.9% | **0.30%** |

**Non-French is not working.** German: 2,670 sessions, 8 leads. English: 5,302 sessions, 35 leads — half the French conversion rate, and zero on mobile.

Roughly 3,000 Apr–Aug sessions come from destination countries (India, Indonesia, Sri Lanka, Thailand, Vietnam, Japan) converting at ~0.2%. Some is local staff and suppliers. Worth segmenting out so it stops diluting every average — but check for genuine expat demand before excluding it.

The `locale` custom dimension confirms the funnel is 95% French: `fr` 1,342 users, `en` 61, `de` 14.

---

## What I'd look at first

1. **The contact step of the inquiry form.** 366 lost leads in two months. Biggest number on this page by a distance.
2. **Mobile on `/fr/voyage-inde` and `/fr/voyage-bali`.** 4–5× worse than desktop on high-traffic pages. Probably the same root cause as #1.
3. **De-duplicate the key events** and split `www` from `connect`. Until then no conversion figure is reportable.
4. **Add a conversion path to `/fr/departs-garantis-petit-groupe`** and surface `/fr/trips`. Two small changes, best-engaging and best-converting pages respectively.
5. **Organic search conversion.** Same traffic as paid, 39% of the rate, and more engaged. Structural, not quick.

---

## Files

- `ga4-deep-dive.json` — curated, dashboard-ready (31 KB)
- `ga4-raw.json` — full API responses, 33 sections (456 KB)
- `ga.py` / `pull.py` / `pull2.py` — re-runnable pull scripts

# Prompt: Monthly SEO Report Update (GSC + Ahrefs via MCP)

Use this prompt at the start of each month's update chat with Claude.
Claude will pull GSC and Ahrefs automatically, then write everything to the sheet.

---

## THE PROMPT (copy everything below this line)

I need to update the Shanti Travel monthly SEO report for [MONTH YEAR].

Google Sheet ID: 18Hb5VIvNsbSRuVh9PNbhNlQ5PwI5AF5Zt_zlVaGDZ8w
Vercel data: I have already pasted the JSON into the sheet tab "vercel_[YYYY-MM]"

Please do the following automatically:
1. Pull GSC data for [MONTH YEAR] from https://www.shantitravel.com/ via MCP
   - Overall: clicks, impressions, CTR, avg position
   - By device (mobile/desktop/tablet)
   - By locale (filter /en/, /de/, rest = FR)
   - Top 50 queries
   - Top 50 pages
   - Top 20 countries
   - Branded vs non-branded (branded = contains "shanti")
2. Pull Ahrefs data for shantitravel.com via MCP
   - Organic traffic estimate (monthly)
   - Domain Rating
   - Referring domains count
   - Live backlinks count
   - Keyword position buckets FR (top3 / 4-10 / 11+)
   - Top 25 keywords by traffic (FR)
   - Top 25 keywords by volume (FR, position ≤ 30)
   - Top 15 keyword gainers vs previous month (volume ≥ 500, position ≤ 30)
   - Top 15 keyword losers vs previous month (volume ≥ 500, prev position ≤ 30)
3. Format all data as JSON matching the report schema
4. Write it to the Google Sheet tab "gsc_[YYYY-MM]" and "ahrefs_[YYYY-MM]"
5. Confirm the report URL is live: https://shanti-rapport.vercel.app

Previous month for MoM comparison: [PREVIOUS MONTH YEAR]


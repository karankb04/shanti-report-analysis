"""
August-only GA4 pull for the ORIGINAL Coupler-fed dashboard tab
(secGA4 / buildChannels in index.html), not the new deep-dive page.

Coupler is being retired, so this replaces it for August 2026 and
future months. Output uses the exact same column-name keys Coupler's
CSV export used ("Dimension: Landing page", "Session: Session
default channel group", etc.) so it drops into data/ga4/<month>.json
and data/ga4ch/<month>.json with zero reshaping and zero dashboard
code changes beyond the two new tab names in tools/write-data.js.

Usage:
    cd ga4-report
    export GA4_KEY="/path/to/key.json"
    python pull_august.py 2026-08          # or any other YYYY-MM
"""
import ga, json, sys, calendar

if len(sys.argv) != 2:
    print("Usage: python pull_august.py YYYY-MM")
    sys.exit(1)

ym = sys.argv[1]
year, month = ym.split('-')
last_day = calendar.monthrange(int(year), int(month))[1]
S, E = f"{ym}-01", f"{ym}-{last_day:02d}"

WWW = {"filter": {"fieldName": "hostName", "stringFilter": {"value": "www.shantitravel.com"}}}

print(f"Pulling {S} .. {E}")

landing_raw = ga.rows(ga.report(
    ['landingPagePlusQueryString'],
    ['sessions', 'totalUsers', 'newUsers', 'engagedSessions', 'engagementRate', 'bounceRate'],
    S, E, limit=1000, order=ga.desc('sessions'), dim_filter=WWW
))
if isinstance(landing_raw, dict):
    print("ERROR landing:", landing_raw); sys.exit(1)
print(f"  landing pages: {len(landing_raw)} rows")

channels_raw = ga.rows(ga.report(
    ['sessionDefaultChannelGroup'],
    ['sessions', 'totalUsers', 'newUsers', 'bounceRate', 'keyEvents'],
    S, E, limit=30, order=ga.desc('sessions'), dim_filter=WWW
))
if isinstance(channels_raw, dict):
    print("ERROR channels:", channels_raw); sys.exit(1)
print(f"  channels: {len(channels_raw)} rows")

landing_rows = [{
    "Dimension: Landing page": r["landingPagePlusQueryString"],
    "Acquisition: Sessions": int(r["sessions"]),
    "Acquisition: New users": int(r["newUsers"]),
    "Acquisition: Total users": int(r["totalUsers"]),
    "Engagement: Engaged sessions": int(r["engagedSessions"]),
    "Engagement: Engagement rate": float(r["engagementRate"]),
    "Performance: Bounce rate": float(r["bounceRate"]),
} for r in landing_raw]

channel_rows = [{
    "Session: Session default channel group": r["sessionDefaultChannelGroup"],
    "Engagement: Sessions": int(r["sessions"]),
    "Acquisition: Total users": int(r["totalUsers"]),
    "Acquisition: New users": int(r["newUsers"]),
    "Engagement: Bounce rate": float(r["bounceRate"]),
    "Key event: Key events": int(r["keyEvents"]),
} for r in channels_raw]

json.dump({"rows": landing_rows}, open(f"ga4_landing_{ym}.json", "w"))
json.dump({"rows": channel_rows}, open(f"ga4_channels_{ym}.json", "w"))
print(f"\nWrote ga4_landing_{ym}.json and ga4_channels_{ym}.json")
print("Share both files in chat - Claude will place them at:")
print(f"  data/ga4/{ym}.json")
print(f"  data/ga4ch/{ym}.json")

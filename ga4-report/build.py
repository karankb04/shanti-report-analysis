import json

d = json.load(open('ga4-raw.json'))


def n(x):
    try:
        return int(x)
    except Exception:
        return 0


def fl(x):
    try:
        return round(float(x), 4)
    except Exception:
        return 0.0


o = {
    "meta": {
        "property_id": "352360511",
        "source": "GA4 Data API v1beta",
        "traffic_window": {"start": "2026-04-01", "end": "2026-08-31"},
        "conversion_window": {"start": "2026-07-01", "end": "2026-08-31"},
        "conversion_window_reason": "Conversion events on www.shantitravel.com first fired in July 2026. April-June contain zero key events.",
        "key_event_inflation_factor": 2.0,
        "key_event_inflation_reason": "inquiry_submitted and demande_voyage_fr both fire per lead on www. Divide reported key events by ~2 for real leads.",
        "domains": {
            "www.shantitravel.com": "marketing site / new business",
            "connect.shantitravel.com": "existing-guest forms and reviews, NOT sales leads",
        },
    }
}

hw, hc = d['headline_www'][0], d['headline_connect'][0]
o['basic_metrics'] = {
    "www": {
        "sessions": n(hw['sessions']),
        "users": n(hw['totalUsers']),
        "new_users": n(hw['newUsers']),
        "new_user_share": round(n(hw['newUsers']) / n(hw['totalUsers']), 4),
        "engagement_rate": fl(hw['engagementRate']),
        "avg_session_seconds": round(float(hw['averageSessionDuration'])),
        "pages_per_session": round(float(hw['screenPageViewsPerSession']), 2),
        "bounce_rate": fl(hw['bounceRate']),
        "key_events_reported": n(hw['keyEvents']),
        "estimated_real_leads": round(n(hw['keyEvents']) / 2),
    },
    "connect": {
        "sessions": n(hc['sessions']),
        "users": n(hc['totalUsers']),
        "engagement_rate": fl(hc['engagementRate']),
        "avg_session_seconds": round(float(hc['averageSessionDuration'])),
        "pages_per_session": round(float(hc['screenPageViewsPerSession']), 2),
        "key_events_reported": n(hc['keyEvents']),
        "estimated_real_guest_submissions": round(n(hc['keyEvents']) / 2),
    },
}

o['monthly_www'] = [
    {
        "month": r['yearMonth'],
        "sessions": n(r['sessions']),
        "users": n(r['totalUsers']),
        "new_users": n(r['newUsers']),
        "engagement_rate": fl(r['engagementRate']),
        "pages_per_session": round(float(r['screenPageViewsPerSession']), 2),
        "key_events_reported": n(r['keyEvents']),
    }
    for r in d['monthly_www']
]

o['channels'] = [
    {
        "channel": r['sessionDefaultChannelGroup'],
        "sessions": n(r['sessions']),
        "engagement_rate": fl(r['engagementRate']),
        "avg_session_seconds": round(float(r['averageSessionDuration'])),
        "pages_per_session": round(float(r['screenPageViewsPerSession']), 2),
        "key_events_reported": n(r['keyEvents']),
        "cvr_reported": round(n(r['keyEvents']) / max(n(r['sessions']), 1), 4),
        "cvr_deduplicated": round(n(r['keyEvents']) / 2 / max(n(r['sessions']), 1), 4),
    }
    for r in d['cw_channels']
]

o['devices'] = [
    {
        "device": r['deviceCategory'],
        "sessions": n(r['sessions']),
        "engagement_rate": fl(r['engagementRate']),
        "key_events_reported": n(r['keyEvents']),
        "cvr_deduplicated": round(n(r['keyEvents']) / 2 / max(n(r['sessions']), 1), 4),
    }
    for r in d['cw_device']
]

steps = [r for r in d['funnel_step_id'] if r['customEvent:step_id'] != '(not set)']
order = ['destinations', 'travelers', 'dates', 'budget', 'stage', 'story', 'contact']
smap = {r['customEvent:step_id']: n(r['totalUsers']) for r in steps}
entrants = smap.get('destinations', 1)
funnel, prev = [], None
for s in order:
    u = smap.get(s, 0)
    funnel.append({
        "step": s,
        "users": u,
        "drop_from_previous": None if prev is None else round((prev - u) / prev, 4),
        "share_of_entrants": round(u / entrants, 4),
    })
    prev = u
contact = smap.get('contact', 1)
funnel.append({
    "step": "submitted",
    "users": 696,
    "drop_from_previous": round((contact - 696) / contact, 4),
    "share_of_entrants": round(696 / entrants, 4),
})
o['inquiry_funnel'] = {
    "window": "2026-07-01..2026-08-31",
    "steps": funnel,
    "entrants": entrants,
    "completions": 696,
    "completion_rate": round(696 / entrants, 4),
    "lost_at_final_step": contact - 696,
}

lp = [r for r in d['cw_landing'] if not r['landingPagePlusQueryString'].startswith('(')]
o['landing_pages'] = [
    {
        "page": r['landingPagePlusQueryString'],
        "sessions": n(r['sessions']),
        "engagement_rate": fl(r['engagementRate']),
        "bounce_rate": fl(r['bounceRate']),
        "avg_session_seconds": round(float(r['averageSessionDuration'])),
        "key_events_reported": n(r['keyEvents']),
        "cvr_deduplicated": round(n(r['keyEvents']) / 2 / max(n(r['sessions']), 1), 4),
    }
    for r in lp[:40]
]

agg = {}
for r in d['cw_device_landing']:
    agg.setdefault(r['landingPagePlusQueryString'], {})[r['deviceCategory']] = (
        n(r['sessions']), fl(r['engagementRate']), n(r['keyEvents'])
    )
gaps = []
for p, v in agg.items():
    m, k = v.get('mobile'), v.get('desktop')
    if not m or not k or m[0] < 80 or k[0] < 50:
        continue
    mc, dc = m[2] / 2 / m[0], k[2] / 2 / k[0]
    gaps.append({
        "page": p,
        "mobile_sessions": m[0], "mobile_cvr": round(mc, 4), "mobile_engagement": m[1],
        "desktop_sessions": k[0], "desktop_cvr": round(dc, 4), "desktop_engagement": k[1],
        "cvr_gap_pp": round((dc - mc) * 100, 2),
    })
o['mobile_desktop_gaps'] = sorted(gaps, key=lambda x: -x['cvr_gap_pp'])[:15]

ai_t = ('chatgpt', 'openai', 'perplexity', 'claude', 'gemini', 'copilot', 'grok', 'deepseek', 'you.com', 'phind')
ai = [r for r in d['cw_ai']
      if any(t in r['sessionSource'].lower() for t in ai_t)
      or r['sessionDefaultChannelGroup'] == 'AI Assistant']
o['ai_traffic'] = sorted(
    [{
        "source": r['sessionSource'],
        "channel_assigned": r['sessionDefaultChannelGroup'],
        "sessions": n(r['sessions']),
        "engagement_rate": fl(r['engagementRate']),
        "avg_session_seconds": round(float(r['averageSessionDuration'])),
        "pages_per_session": round(float(r['screenPageViewsPerSession']), 2),
        "key_events_reported": n(r['keyEvents']),
    } for r in ai],
    key=lambda x: -x['sessions'])

o['geography'] = [
    {"country": r['country'], "sessions": n(r['sessions']), "engagement_rate": fl(r['engagementRate']),
     "key_events_reported": n(r['keyEvents']),
     "cvr_deduplicated": round(n(r['keyEvents']) / 2 / max(n(r['sessions']), 1), 4)}
    for r in d['cw_country'][:15]
]
o['languages'] = [
    {"language": r['language'], "sessions": n(r['sessions']), "engagement_rate": fl(r['engagementRate']),
     "key_events_reported": n(r['keyEvents']),
     "cvr_deduplicated": round(n(r['keyEvents']) / 2 / max(n(r['sessions']), 1), 4)}
    for r in d['cw_language'][:10]
]

h1 = {r['landingPagePlusQueryString']: (n(r['sessions']), fl(r['engagementRate'])) for r in d['decay_h1']}
h2 = {r['landingPagePlusQueryString']: (n(r['sessions']), fl(r['engagementRate'])) for r in d['decay_h2']}
tr = []
for p, (s1, e1) in h1.items():
    if s1 < 150 or p.startswith('('):
        continue
    s2, e2 = h2.get(p, (0, 0.0))
    tr.append({"page": p, "sessions_apr1_jun15": s1, "sessions_jun16_aug31": s2,
               "change_pct": round((s2 - s1) / s1 * 100, 1),
               "engagement_before": e1, "engagement_after": e2})
tr.sort(key=lambda x: x['change_pct'])
o['content_trend'] = {"losing": tr[:10], "gaining": tr[-10:][::-1]}

o['data_quality_issues'] = [
    {"id": "conversion_tracking_gap", "severity": "critical",
     "detail": "No key events fired on www before July 2026. April-June 2026 conversion data does not exist.",
     "evidence": {"key_events_by_month": {"202604": 0, "202605": 0, "202606": 0, "202607": 401, "202608": 1032}}},
    {"id": "duplicate_conversion_events", "severity": "critical",
     "detail": "inquiry_submitted (735 events / 696 users) and demande_voyage_fr (706 / 668) both fire per lead on www. Both are marked as key events.",
     "impact": "All reported conversion counts on www are roughly 2x actual leads."},
    {"id": "two_businesses_in_one_number", "severity": "critical",
     "detail": "connect.shantitravel.com handles existing-guest forms and reviews, not sales leads, but its submissions are counted as key events.",
     "evidence": {"property_key_events": 4085, "www_key_events": 1433, "connect_key_events": 2652, "non_lead_share": 0.649}},
    {"id": "junk_traffic", "severity": "medium",
     "detail": "826 Jul-Aug sessions have landing page (not set) with 4 percent engagement and 96 percent bounce. Separately 3,015 Apr-Aug sessions have newVsReturning (not set) at 0.4 percent engagement.",
     "impact": "Deflates site-wide engagement and conversion rates."},
    {"id": "dev_traffic_in_production", "severity": "low",
     "detail": "localhost, Vercel preview deployments and translate.goog appear as hostnames in the production property, roughly 90 sessions."},
    {"id": "perplexity_misclassified", "severity": "low",
     "detail": "Perplexity sessions land in Unassigned, not the native AI Assistant channel. Known GA4 gap."},
    {"id": "cross_domain_attribution", "severity": "medium",
     "detail": "connect.shantitravel.com starts its own sessions with source (direct) and (not set) rather than continuing sessions from www."},
]

json.dump(o, open('ga4-deep-dive.json', 'w'), indent=1, ensure_ascii=False)
print("wrote ga4-deep-dive.json")
for s in o['inquiry_funnel']['steps']:
    print(" ", s)

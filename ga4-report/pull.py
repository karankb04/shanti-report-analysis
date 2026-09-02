import ga, json
S, E = '2026-04-01', '2026-08-31'
WWW = {"filter": {"fieldName": "hostName", "stringFilter": {"value": "www.shantitravel.com"}}}
CON = {"filter": {"fieldName": "hostName", "stringFilter": {"value": "connect.shantitravel.com"}}}
out = {"window": {"start": S, "end": E}, "property": "352360511"}

def R(name, dims, mets, limit=100, order=None, filt=None, s=S, e=E):
    res = ga.rows(ga.report(dims, mets, s, e, limit=limit, order=order, dim_filter=filt))
    if isinstance(res, dict):
        print("  ERR", name, res.get("_error"), str(res.get("_body"))[:300]); return []
    out[name] = res
    print(f"  ok {name} ({len(res)} rows)")
    return res

CORE = ['sessions','totalUsers','newUsers','engagedSessions','engagementRate',
        'averageSessionDuration','screenPageViewsPerSession','bounceRate','keyEvents']

print("A. headline")
R('headline_www', [], CORE, filt=WWW)
R('headline_connect', [], CORE, filt=CON)
R('headline_all', [], CORE)

print("B. monthly trend")
R('monthly_www', ['yearMonth'], CORE, limit=24,
  order=[{"dimension":{"dimensionName":"yearMonth"},"desc":False}], filt=WWW)

print("C. hostname split")
R('hosts', ['hostName'], ['sessions','totalUsers','keyEvents'], limit=40, order=ga.desc('sessions'))

print("D. channels")
R('channels_www', ['sessionDefaultChannelGroup'],
  ['sessions','totalUsers','newUsers','engagementRate','averageSessionDuration',
   'screenPageViewsPerSession','keyEvents'], limit=30, order=ga.desc('sessions'), filt=WWW)

print("E. source/medium")
R('source_medium_www', ['sessionSource','sessionMedium'],
  ['sessions','engagementRate','keyEvents'], limit=60, order=ga.desc('sessions'), filt=WWW)

print("F. campaigns (unassigned diagnosis)")
R('campaigns_www', ['sessionCampaignName','sessionSource','sessionMedium'],
  ['sessions','keyEvents'], limit=40, order=ga.desc('sessions'), filt=WWW)

print("G. landing pages")
R('landing_www', ['landingPagePlusQueryString'],
  ['sessions','totalUsers','engagementRate','averageSessionDuration',
   'screenPageViewsPerSession','bounceRate','keyEvents'],
  limit=150, order=ga.desc('sessions'), filt=WWW)

print("H. device")
R('device_www', ['deviceCategory'],
  ['sessions','engagementRate','averageSessionDuration','screenPageViewsPerSession','keyEvents'],
  limit=10, order=ga.desc('sessions'), filt=WWW)
R('device_landing_www', ['landingPagePlusQueryString','deviceCategory'],
  ['sessions','engagementRate','keyEvents'], limit=300, order=ga.desc('sessions'), filt=WWW)

print("I. inquiry funnel")
R('funnel_step_index', ['customEvent:step_index'], ['eventCount','totalUsers'], limit=50,
  order=[{"dimension":{"dimensionName":"customEvent:step_index"},"desc":False}], filt=WWW)
R('funnel_step_id', ['customEvent:step_id'], ['eventCount','totalUsers'], limit=60,
  order=ga.desc('eventCount'), filt=WWW)

print("J. geo / language")
R('country_www', ['country'], ['sessions','engagementRate','keyEvents'], limit=30,
  order=ga.desc('sessions'), filt=WWW)
R('language_www', ['language'], ['sessions','engagementRate','keyEvents'], limit=30,
  order=ga.desc('sessions'), filt=WWW)
R('locale_www', ['customEvent:locale'], ['eventCount','totalUsers'], limit=30,
  order=ga.desc('eventCount'), filt=WWW)

print("K. AI traffic")
R('ai_sources_www', ['sessionSource','sessionDefaultChannelGroup'],
  ['sessions','engagementRate','averageSessionDuration','screenPageViewsPerSession','keyEvents'],
  limit=200, order=ga.desc('sessions'), filt=WWW)

print("L. decay halves")
for tag, a, b in [('h1','2026-04-01','2026-06-15'), ('h2','2026-06-16','2026-08-31')]:
    res = ga.rows(ga.report(['landingPagePlusQueryString'], ['sessions','engagementRate','keyEvents'],
                            a, b, limit=150, order=ga.desc('sessions'), dim_filter=WWW))
    out[f'decay_{tag}'] = res if not isinstance(res, dict) else []
    print(f"  ok decay_{tag} ({len(out[f'decay_{tag}'])} rows)")

print("M. new vs returning")
R('new_returning_www', ['newVsReturning'], ['sessions','engagementRate','keyEvents'],
  limit=10, order=ga.desc('sessions'), filt=WWW)

print("N. day of week / hour")
R('hour_www', ['hour'], ['sessions','keyEvents'], limit=24,
  order=[{"dimension":{"dimensionName":"hour"},"desc":False}], filt=WWW)

json.dump(out, open('ga4-raw.json','w'), indent=1)
print("\nWROTE ga4-raw.json —", len(out), "sections")

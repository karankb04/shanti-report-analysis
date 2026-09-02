import ga, json
WWW = {"filter": {"fieldName": "hostName", "stringFilter": {"value": "www.shantitravel.com"}}}
CORE = ['sessions','totalUsers','newUsers','engagedSessions','engagementRate',
        'averageSessionDuration','screenPageViewsPerSession','bounceRate','keyEvents']
out = json.load(open('ga4-raw.json'))
PY_S, PY_E = '2025-04-01', '2025-08-31'

def R(name, dims, mets, s, e, limit=100, order=None, filt=WWW):
    res = ga.rows(ga.report(dims, mets, s, e, limit=limit, order=order, dim_filter=filt))
    if isinstance(res, dict):
        print("  ERR", name, res.get('_error'), str(res.get('_body'))[:200]); return
    out[name] = res; print(f"  ok {name} ({len(res)} rows)")

R('py_headline', [], CORE, PY_S, PY_E)
R('py_monthly', ['yearMonth'], CORE, PY_S, PY_E, limit=12,
  order=[{"dimension":{"dimensionName":"yearMonth"},"desc":False}])
R('py_channels', ['sessionDefaultChannelGroup'],
  ['sessions','totalUsers','engagementRate','averageSessionDuration','screenPageViewsPerSession','keyEvents'],
  PY_S, PY_E, limit=30, order=ga.desc('sessions'))
R('py_landing', ['landingPagePlusQueryString'], ['sessions','engagementRate','bounceRate'],
  PY_S, PY_E, limit=120, order=ga.desc('sessions'))
R('py_device', ['deviceCategory'], ['sessions','engagementRate'], PY_S, PY_E, limit=10, order=ga.desc('sessions'))
R('py_country', ['country'], ['sessions','engagementRate'], PY_S, PY_E, limit=25, order=ga.desc('sessions'))
R('py_language', ['language'], ['sessions','engagementRate'], PY_S, PY_E, limit=15, order=ga.desc('sessions'))
R('py_events', ['eventName'], ['eventCount','totalUsers'], PY_S, PY_E, limit=40, order=ga.desc('eventCount'))
# monthly channel detail for current year MoM
R('cy_monthly_channels', ['yearMonth','sessionDefaultChannelGroup'], ['sessions','keyEvents'],
  '2026-04-01', '2026-08-31', limit=200)
R('py_monthly_channels', ['yearMonth','sessionDefaultChannelGroup'], ['sessions'],
  PY_S, PY_E, limit=200)
json.dump(out, open('ga4-raw.json','w'), indent=1)
print("saved")

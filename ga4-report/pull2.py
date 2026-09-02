import ga, json
CS, CE = '2026-07-01', '2026-08-31'   # conversion-valid window
WWW = {"filter": {"fieldName": "hostName", "stringFilter": {"value": "www.shantitravel.com"}}}
out = json.load(open('ga4-raw.json'))
out['conversion_window'] = {"start": CS, "end": CE, "note": "conversion tracking on www began July 2026"}

def R(name, dims, mets, limit=100, order=None):
    res = ga.rows(ga.report(dims, mets, CS, CE, limit=limit, order=order, dim_filter=WWW))
    if isinstance(res, dict):
        print("  ERR", name, res.get('_error'), str(res.get('_body'))[:300]); return
    out[name] = res; print(f"  ok {name} ({len(res)} rows)")

R('cw_channels', ['sessionDefaultChannelGroup'],
  ['sessions','engagementRate','averageSessionDuration','screenPageViewsPerSession','keyEvents'],
  limit=30, order=ga.desc('sessions'))
R('cw_source', ['sessionSource','sessionMedium'], ['sessions','engagementRate','keyEvents'],
  limit=80, order=ga.desc('sessions'))
R('cw_landing', ['landingPagePlusQueryString'],
  ['sessions','totalUsers','engagementRate','averageSessionDuration','bounceRate','keyEvents'],
  limit=200, order=ga.desc('sessions'))
R('cw_device', ['deviceCategory'], ['sessions','engagementRate','keyEvents'], limit=10, order=ga.desc('sessions'))
R('cw_device_landing', ['landingPagePlusQueryString','deviceCategory'],
  ['sessions','engagementRate','keyEvents'], limit=400, order=ga.desc('sessions'))
R('cw_country', ['country'], ['sessions','engagementRate','keyEvents'], limit=30, order=ga.desc('sessions'))
R('cw_language', ['language'], ['sessions','engagementRate','keyEvents'], limit=20, order=ga.desc('sessions'))
R('cw_ai', ['sessionSource','sessionDefaultChannelGroup'],
  ['sessions','engagementRate','averageSessionDuration','screenPageViewsPerSession','keyEvents'],
  limit=200, order=ga.desc('sessions'))
R('cw_campaign', ['sessionCampaignName','sessionMedium'], ['sessions','keyEvents'], limit=50, order=ga.desc('sessions'))
R('cw_headline', [], ['sessions','totalUsers','engagementRate','keyEvents'], limit=1)

json.dump(out, open('ga4-raw.json','w'), indent=1)
print("updated ga4-raw.json")

"""Minimal GA4 Data API client. Reads key path from GA4_KEY env var; never prints it."""
import os, json, sys
from google.oauth2 import service_account
import google.auth.transport.requests as gart
import requests

KEY = os.environ["GA4_KEY"]
PROP = os.environ.get("GA4_PROPERTY", "352360511")
SCOPE = ["https://www.googleapis.com/auth/analytics.readonly"]
BASE = f"https://analyticsdata.googleapis.com/v1beta/properties/{PROP}"

_sess = None
def _token():
    global _sess
    if _sess is None:
        creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPE)
        creds.refresh(gart.Request())
        _sess = creds
    return _sess.token

def call(endpoint, body=None):
    url = f"{BASE}:{endpoint}" if endpoint != "metadata" else f"{BASE}/metadata"
    h = {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"}
    r = requests.post(url, headers=h, json=body) if body is not None else requests.get(url, headers=h)
    if r.status_code != 200:
        return {"_error": r.status_code, "_body": r.text[:1200]}
    return r.json()

def report(dims, mets, start, end, limit=50, order=None, dim_filter=None, met_filter=None, keep_empty=False):
    body = {
        "dateRanges": [{"startDate": start, "endDate": end}],
        "dimensions": [{"name": d} for d in dims],
        "metrics": [{"name": m} for m in mets],
        "limit": limit,
        "keepEmptyRows": keep_empty,
    }
    if order: body["orderBys"] = order
    if dim_filter: body["dimensionFilter"] = dim_filter
    if met_filter: body["metricFilter"] = met_filter
    return call("runReport", body)

def rows(res):
    """Flatten a runReport response into list of dicts."""
    if "_error" in res: return res
    dh = [d["name"] for d in res.get("dimensionHeaders", [])]
    mh = [m["name"] for m in res.get("metricHeaders", [])]
    out = []
    for r in res.get("rows", []):
        rec = {}
        for i, v in enumerate(r.get("dimensionValues", [])): rec[dh[i]] = v.get("value")
        for i, v in enumerate(r.get("metricValues", [])): rec[mh[i]] = v.get("value")
        out.append(rec)
    return out

def desc(metric):
    return [{"metric": {"metricName": metric}, "desc": True}]

#!/usr/bin/env python3
"""
Google search through the Bright Data SERP API — for agents without a built-in search tool.
Needs BRIGHTDATA_API_KEY (and optionally BRIGHTDATA_ZONE) in the environment or ~/.ai-sales-team/.env.
If you don't have a key, use your agent's own web search instead; skills never require this script.

Usage:
    python web_search.py "acme corp funding 2026" [--lookback 30] [--country in] [--num 10]
"""

import argparse
import sys
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
from sales_common import ApiError, api_json, emit, secret  # noqa: E402


def search(query, lookback=None, country="", num=10, call=api_json):
    key = secret("BRIGHTDATA_API_KEY")
    if not key:
        raise ApiError(0, "BRIGHTDATA_API_KEY not set — use your agent's own web search, or add the key to ~/.ai-sales-team/.env")
    params = {"q": query, "num": num, "hl": "en"}
    if lookback:
        params["tbs"] = "qdr:w" if lookback == 7 else f"qdr:d{int(lookback)}"
    if country:
        params["gl"] = country
    body = {"zone": secret("BRIGHTDATA_ZONE") or "serp_api1", "url": "https://www.google.com/search?" + urlencode(params),
            "format": "raw", "data_format": "parsed_light"}
    status, data = call("POST", "https://api.brightdata.com/request", headers={"Authorization": f"Bearer {key}"}, body=body, timeout=60)
    if status >= 400 or not isinstance(data, dict) or "organic" not in data:
        raise ApiError(status, f"Bright Data error (HTTP {status}): {str(data)[:200]}")
    return [{"title": r.get("title"), "url": r.get("link"), "snippet": r.get("description")} for r in data["organic"] if r.get("link")]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Google search via Bright Data SERP API.")
    ap.add_argument("query")
    ap.add_argument("--lookback", type=int, help="only results from the last N days")
    ap.add_argument("--country", default="")
    ap.add_argument("--num", type=int, default=10)
    a = ap.parse_args(argv)
    try:
        emit({"ok": True, "data": {"query": a.query, "results": search(a.query, a.lookback, a.country, a.num)}})
    except ApiError as exc:
        emit({"ok": False, "error": str(exc)}, 2 if exc.status == 0 else 4)


if __name__ == "__main__":
    main()

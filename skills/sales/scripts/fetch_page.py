#!/usr/bin/env python3
"""
Fetch a web page and print what an agent needs: title, meta, headings, visible text, links and
JSON-LD. Lets every skill work in agents that have no built-in web tool. Standard library only.
robots.txt is respected.

Usage:
    python fetch_page.py https://acme.com [--max-chars 12000] [--links]
    python fetch_page.py https://acme.com/about https://acme.com/pricing     # several pages, fetched in parallel
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sales_common import base_of, emit, fetch_many, normalize_url, parse_html  # noqa: E402


def page(result, max_chars, with_links):
    out = {"url": result["url"], "final_url": result.get("final_url"), "status": result.get("status"),
           "error": result.get("error")}
    if not result.get("html"):
        return out
    p = parse_html(result["html"])
    out.update({"title": p.title.strip(), "description": p.meta.get("description") or p.meta.get("og:description"),
                "headings": [f"{h['level']}: {h['text']}" for h in p.headings[:40]],
                "text": p.text[:max_chars], "truncated": len(p.text) > max_chars,
                "json_ld_types": sorted({str(i.get("@type")) for i in p.json_ld()})})
    if with_links:
        out["links"] = [{"text": l["text"][:80], "href": l["href"]} for l in p.links if l["href"]][:150]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fetch pages as clean text + structure (robots.txt respected).")
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--max-chars", type=int, default=12000)
    ap.add_argument("--links", action="store_true", help="include links")
    a = ap.parse_args(argv)
    from site_audit import Robots
    urls = [normalize_url(u) for u in a.urls]
    robots = {}
    allowed, blocked = [], []
    for u in urls:
        b = base_of(u)
        robots.setdefault(b, Robots(b))
        (allowed if robots[b].allowed(u) else blocked).append(u)
    pages = [page(r, a.max_chars, a.links) for r in fetch_many(allowed)]
    pages += [{"url": u, "error": "robots.txt disallows this page — not fetched"} for u in blocked]
    emit({"ok": any(p.get("status") == 200 for p in pages), "data": pages[0] if len(pages) == 1 else pages})


if __name__ == "__main__":
    main()

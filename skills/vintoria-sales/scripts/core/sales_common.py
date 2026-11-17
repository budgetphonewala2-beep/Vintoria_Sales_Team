#!/usr/bin/env python3
"""
Shared helpers for the AI Sales Team scripts: polite HTTP fetching, visible-text
extraction, JSON-LD parsing, and soft-404 detection. Standard library only.
"""

import hashlib
import json
import re
import ssl
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 AISalesTeam/2.0"
)
MAX_BYTES = 4 * 1024 * 1024  # never read more than 4 MB of a page


def tls_context():
    """Verified TLS context: the certifi CA bundle when installed (fixes Windows/macOS Pythons that
    can't find the local issuer), else the system store."""
    try:
        import certifi  # optional
        return ssl.create_default_context(cafile=certifi.where())
    except (ImportError, OSError):
        return ssl.create_default_context()


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

def normalize_url(url):
    """Ensure the URL has a scheme. Handles 'example.com' and 'example.com:8080'."""
    url = url.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "https://" + url
    return url


def base_of(url):
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def domain_slug(url):
    """'https://www.Acme.com/about' -> 'acme.com' (used for prospects/<slug>/ folders)."""
    host = urlparse(normalize_url(url)).hostname or ""
    host = host.lower()
    return host[4:] if host.startswith("www.") else host


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def fetch_url(url, timeout=10):
    """
    Fetch a URL. Returns a dict:
      {"url", "final_url", "status", "html", "error", "tls_error"}
    TLS certificates are always verified. There is no unverified fallback: a page we
    can't verify is reported as unreachable (tls_error=True), never fetched insecurely.
    A verification failure is usually the auditing machine's CA store (fix: pip install
    certifi), so callers must not report it as a fact about the prospect.
    """
    result = {"url": url, "final_url": url, "status": None, "html": None,
              "error": None, "tls_error": False}
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
        "Accept-Language": "en-US,en;q=0.8",
    }

    def _do(ctx):
        req = Request(url, headers=headers)
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            result["status"] = resp.status
            result["final_url"] = resp.geturl()
            ctype = resp.headers.get("Content-Type", "")
            if ctype and "html" not in ctype and "xml" not in ctype and "text" not in ctype:
                result["error"] = f"non-HTML content ({ctype})"
                return
            raw = resp.read(MAX_BYTES)
            charset = resp.headers.get_content_charset() or "utf-8"
            result["html"] = raw.decode(charset, errors="replace")

    try:
        _do(tls_context())
    except HTTPError as exc:
        result["status"] = exc.code
        result["error"] = f"HTTP {exc.code}"
    except URLError as exc:
        reason = getattr(exc, "reason", exc)
        if isinstance(reason, ssl.SSLError) or "CERTIFICATE" in str(reason).upper():
            result["tls_error"] = True
            result["error"] = ("TLS certificate could not be verified (not fetched). If many sites fail, "
                               "this machine's CA store is the problem: pip install certifi")
        else:
            result["error"] = f"URLError: {reason}"
    except Exception as exc:  # noqa: BLE001 - timeouts, resets, decode errors
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def fetch_many(urls, timeout=8, workers=6):
    """Fetch several URLs concurrently. Returns results in the same order."""
    if not urls:
        return []
    with ThreadPoolExecutor(max_workers=min(workers, len(urls))) as pool:
        return list(pool.map(lambda u: fetch_url(u, timeout=timeout), urls))


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

_SKIP_TAGS = {"script", "style", "noscript", "svg", "template", "iframe", "head"}
_BLOCK_TAGS = {"p", "div", "li", "td", "th", "tr", "br", "section", "article",
               "header", "footer", "h1", "h2", "h3", "h4", "h5", "h6", "button",
               "dt", "dd", "ul", "ol", "nav", "main", "aside", "figure",
               "figcaption", "blockquote", "form", "table", "hr"}


_INLINE = "\x00"  # marker for inline element boundaries (dropped in .text, split in .element_lines)


class PageParser(HTMLParser):
    """Collects title, meta tags, headings, links, script srcs, JSON-LD and visible text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta = {}
        self.headings = []        # [{"level": "h1", "text": "..."}]
        self.links = []           # [{"href": ..., "text": ...}]
        self.scripts = []
        self.json_ld_raw = []
        self.img_alts = []
        self._text = None
        self.chunks = []          # visible text chunks in document order
        self._skip_depth = 0
        self._in_title = False
        self._ld_buf = None
        self._heading = None      # [level, [text parts]]
        self._link = None         # [href, [text parts]]

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "script":
            if a.get("src"):
                self.scripts.append(a["src"])
            if "ld+json" in a.get("type", "").lower():
                self._ld_buf = []
            self._skip_depth += 1
            return
        if tag in _SKIP_TAGS:
            if tag == "head":
                return  # keep parsing head for title/meta; text in head is not visible anyway
            self._skip_depth += 1
            return
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or a.get("itemprop") or "").lower()
            if key and a.get("content"):
                self.meta.setdefault(key, a["content"].strip())
        elif tag in ("h1", "h2", "h3", "h4"):
            self._heading = [tag, []]
        elif tag == "a":
            self._link = [a.get("href", ""), []]
        elif tag == "img" and a.get("alt") and not self._skip_depth:
            self.img_alts.append(_squash(a["alt"]))
        self.chunks.append("\n" if tag in _BLOCK_TAGS else _INLINE)

    def handle_endtag(self, tag):
        if tag == "script":
            if self._ld_buf is not None:
                self.json_ld_raw.append("".join(self._ld_buf))
                self._ld_buf = None
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if tag in _SKIP_TAGS and tag != "head":
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if tag == "title":
            self._in_title = False
        elif self._heading and tag == self._heading[0]:
            text = _squash(" ".join(self._heading[1]))
            if text:
                self.headings.append({"level": tag, "text": text})
            self._heading = None
        elif tag == "a" and self._link:
            self.links.append({"href": self._link[0], "text": _squash(" ".join(self._link[1]))})
            self._link = None
        self.chunks.append("\n" if tag in _BLOCK_TAGS else _INLINE)

    def handle_data(self, data):
        if self._ld_buf is not None:
            self._ld_buf.append(data)
            return
        if self._in_title:
            self.title += data
            return
        if self._skip_depth:
            return
        self.chunks.append(data)
        if self._heading:
            self._heading[1].append(data)
        if self._link:
            self._link[1].append(data)

    # -- derived views --------------------------------------------------
    @property
    def text(self):
        """Visible text as a browser would join it, one block element per line."""
        if self._text is None:
            raw = "".join(self.chunks).replace(_INLINE, "")
            lines = (_squash(l) for l in raw.split("\n"))
            self._text = "\n".join(l for l in lines if l)
        return self._text

    @property
    def lines(self):
        return self.text.split("\n") if self.text else []

    @property
    def element_lines(self):
        """Visible text split at EVERY element boundary (inline ones too). Used for team cards
        where name and title sit in adjacent <span>s with no whitespace between them."""
        raw = "".join(self.chunks).replace(_INLINE, "\n")
        return [l for l in (_squash(x) for x in raw.split("\n")) if l]

    def json_ld(self):
        """All JSON-LD objects, flattened (handles lists and @graph)."""
        out = []
        for raw in self.json_ld_raw:
            try:
                data = json.loads(raw.strip())
            except (json.JSONDecodeError, ValueError):
                continue
            stack = data if isinstance(data, list) else [data]
            while stack:
                item = stack.pop(0)
                if isinstance(item, dict):
                    if "@graph" in item and isinstance(item["@graph"], list):
                        stack.extend(item["@graph"])
                    out.append(item)
                elif isinstance(item, list):
                    stack.extend(item)
        return out


def _squash(s):
    return re.sub(r"\s+", " ", unescape(s or "")).strip()


def parse_html(html):
    p = PageParser()
    try:
        p.feed(html or "")
        p.close()
    except Exception:  # noqa: BLE001 - malformed HTML should never crash analysis
        pass
    return p


def ld_types(item):
    t = item.get("@type", "")
    return [x.lower() for x in (t if isinstance(t, list) else [t]) if isinstance(x, str)]


def text_fingerprint(parsed):
    """Hash of visible text, used to detect SPA catch-all routes (soft 404s)."""
    return hashlib.sha1(parsed.text.encode("utf-8", "ignore")).hexdigest()


def looks_like_soft_404(parsed, home_fingerprint):
    """A subpage that renders the exact homepage, or says 'not found', is not a real page."""
    if text_fingerprint(parsed) == home_fingerprint:
        return True
    head = (parsed.title + " " + " ".join(h["text"] for h in parsed.headings[:2])).lower()
    return bool(re.search(r"\b(404|page not found|not found|doesn.t exist)\b", head))


def subpage_urls(base, paths):
    return [urljoin(base + "/", p.lstrip("/")) for p in paths]


# ---------------------------------------------------------------------------
# Data home, secrets, JSON APIs (used by the pipeline, hunt and email scripts)
# ---------------------------------------------------------------------------

import os
import sys
import time
from pathlib import Path

_SECRETS = set()


def data_home():
    """User data folder (survives reinstalls): $AI_SALES_HOME or ~/.ai-sales-team."""
    env = os.environ.get("AI_SALES_HOME")
    home = Path(env).expanduser() if env else Path.home() / ".ai-sales-team"
    home.mkdir(parents=True, exist_ok=True)
    return home


def _dotenv():
    path = data_home() / ".env"
    out = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            if v:
                out[k.strip()] = v
    return out


# Settings that live in the seller profile (SELLER-PROFILE.json) when not set in the environment / .env.
PROFILE_SETTINGS = {"SENDER_NAME": "seller.name", "SENDER_EMAIL": "seller.email", "SENDER_ADDRESS": "seller.postal_address",
                    "BOOKING_URL": "seller.booking_url", "MEETING_LINK": "seller.meeting_link", "TIMEZONE": "seller.timezone"}


def _profile_value(dotted):
    for path in (Path("SELLER-PROFILE.json"), data_home() / "seller-profile.json"):
        if path.exists():
            try:
                cur = json.loads(path.read_text(encoding="utf-8-sig"))
            except ValueError:
                return None
            for part in dotted.split("."):
                cur = cur.get(part) if isinstance(cur, dict) else None
            return cur if isinstance(cur, str) and cur.strip() else None
    return None


def setting(name, default=None):
    """Non-secret setting from the environment, <data home>/.env, or (sender/booking/time zone) the seller profile."""
    value = os.environ.get(name) or _dotenv().get(name)
    if not value and name in PROFILE_SETTINGS:
        value = _profile_value(PROFILE_SETTINGS[name])
    return value if value else default


def secret(name):
    """API key from the environment or <data home>/.env; registered for redaction. None if unset."""
    value = os.environ.get(name) or _dotenv().get(name)
    if value and len(value) >= 6:
        _SECRETS.add(value)
    return value or None


def redact(text):
    s = str(text)
    for v in sorted(_SECRETS, key=len, reverse=True):
        s = s.replace(v, "***")
    return s


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def api_json(method, url, headers=None, body=None, params=None, timeout=30, retries=2, sleep=time.sleep):
    """JSON API call with retry on 429/5xx (Retry-After aware). Returns (status, parsed_json)."""
    from urllib.parse import urlencode
    if params:
        url = url + ("&" if "?" in url else "?") + urlencode(params)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    hdrs = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if data is not None:
        hdrs["Content-Type"] = "application/json"
    hdrs.update(headers or {})
    attempt = 0
    while True:
        attempt += 1
        req = Request(url, data=data, headers=hdrs, method=method.upper())
        try:
            with urlopen(req, timeout=timeout, context=tls_context()) as resp:
                raw = resp.read(MAX_BYTES)
                status = resp.status
        except HTTPError as exc:
            raw, status = exc.read() or b"", exc.code
            if status in (429, 500, 502, 503, 504) and attempt <= retries:
                wait = exc.headers.get("Retry-After") if exc.headers else None
                sleep(min(float(wait), 30.0) if wait and wait.isdigit() else 1.5 * attempt)
                continue
        except URLError as exc:
            raise ApiError(0, redact(f"network error: {getattr(exc, 'reason', exc)}"))
        try:
            parsed = json.loads(raw.decode("utf-8-sig")) if raw else {}
        except ValueError:
            parsed = {"raw": raw[:300].decode("utf-8", "replace")}
        return status, parsed


def emit(obj, code=0):
    """Print one JSON object (secrets redacted) and exit."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    print(redact(json.dumps(obj, ensure_ascii=False, indent=2, default=str)))
    sys.exit(code)

#!/usr/bin/env python3
"""Check that every link in a deliverable opens.

Usage:
    python check_links.py file [more files] [--timeout 15]

Reads Markdown, CSV or plain-text files (for example a brief, a pack or an evidence pages log),
finds every http(s) link and requests it. Each link is reported as:

    OK            the page answered (2xx, or a redirect that ends in 2xx)
    BROKEN        404 or 410: the page is gone; fix or remove the link
    ERROR         another 4xx or 5xx, a timeout or no connection: open it by hand
    CHECK BY HAND a LinkedIn link that did not come back 404: LinkedIn blocks scripts
                  (999 or 403) or shows a login wall that still answers 200, so a
                  person must open it in a browser and confirm the profile

A link is checked once even if it appears many times. The script only says whether a
page opens. It cannot say whether the page shows what the deliverable claims (the right
person, the right job post, a date): that still needs a person.

Exit code: 0 when every link is OK or CHECK BY HAND, 1 when any is BROKEN or ERROR,
2 on a usage error.
"""

import csv
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

URL = re.compile(r"https?://[^\s<>\"'`|)\]]+")
TRAILING = ".,;:!?*_"
BY_HAND_HOSTS = ("linkedin.com",)
UA = "Mozilla/5.0 (compatible; link-check)"


def die(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(2)


def extract_urls(text):
    """Return the unique links in text, in order of first appearance."""
    seen, out = set(), []
    for m in URL.finditer(text):
        u = m.group(0).rstrip(TRAILING)
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def read_text(path):
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            raw = f.read()
    except OSError as e:
        die(f"cannot read {path}: {e.strerror}")
    if path.lower().endswith(".csv"):
        try:
            rows = csv.reader(raw.splitlines())
            return "\n".join(" ".join(r) for r in rows)
        except csv.Error:
            return raw
    return raw


def classify(url, status, error=None):
    """Turn an HTTP status (or a connection error) into a verdict."""
    host = urllib.parse.urlparse(url).netloc.lower()
    blocked = any(host == h or host.endswith("." + h) for h in BY_HAND_HOSTS)
    if blocked and status not in (404, 410):
        return "CHECK BY HAND"
    if error:
        return "ERROR"
    if 200 <= status < 300:
        return "OK"
    if status in (404, 410):
        return "BROKEN"
    return "ERROR"


def fetch(url, timeout):
    """Return (status, error). Tries HEAD first, then GET when HEAD is refused."""
    last = None
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, None
        except urllib.error.HTTPError as e:
            last = (e.code, None)
            if method == "HEAD" and e.code in (403, 405, 501):
                continue
            return last
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            reason = getattr(e, "reason", e)
            last = (0, str(reason))
            if method == "HEAD":
                continue
    return last


def main(argv):
    timeout = 15
    if "--timeout" in argv:
        i = argv.index("--timeout")
        try:
            timeout = float(argv[i + 1])
        except (IndexError, ValueError):
            die("--timeout needs a number of seconds")
        del argv[i:i + 2]
    if not argv:
        die("usage: check_links.py file [more files] [--timeout 15]")
    urls = []
    for path in argv:
        if not os.path.isfile(path):
            die(f"not a file: {path}")
        for u in extract_urls(read_text(path)):
            if u not in urls:
                urls.append(u)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    counts = {}
    for u in urls:
        status, error = fetch(u, timeout)
        verdict = classify(u, status, error)
        counts[verdict] = counts.get(verdict, 0) + 1
        detail = error or str(status)
        print(f"{verdict:<14} {detail:<6} {u}")
    bad = counts.get("BROKEN", 0) + counts.get("ERROR", 0)
    print(f"\n{len(urls)} link(s): " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
          if urls else "\nNo links found.")
    if counts.get("CHECK BY HAND"):
        print("Open every CHECK BY HAND link in a browser: the site blocks automated checks.")
    if bad:
        print("Fix or remove every BROKEN link, and open every ERROR link by hand.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

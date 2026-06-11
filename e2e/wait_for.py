#!/usr/bin/env python3
"""Poll HTTP endpoints until healthy (or time out).

Used by the runner / Makefile so the e2e harness does not race container
startup. Pure standard library — no dependency inside the wait step.

Usage:
    python e2e/wait_for.py http://localhost:8000/ http://localhost:8069/web/login
    python e2e/wait_for.py --timeout 600 --interval 5 URL [URL ...]
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request


def is_up(url: str, timeout: float = 5.0) -> bool:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # Any HTTP response (even 3xx/4xx login redirects) means the
            # service is accepting connections — that is "up" for our purposes.
            return 200 <= resp.status < 500
    except urllib.error.HTTPError as exc:
        return 200 <= exc.code < 500
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--timeout", type=float, default=600.0, help="seconds")
    ap.add_argument("--interval", type=float, default=5.0, help="seconds")
    args = ap.parse_args()

    deadline = time.time() + args.timeout
    pending = list(args.urls)
    while pending and time.time() < deadline:
        still = []
        for url in pending:
            if is_up(url):
                print(f"[wait_for] up: {url}")
            else:
                still.append(url)
        pending = still
        if pending:
            time.sleep(args.interval)

    if pending:
        print(f"[wait_for] TIMEOUT after {args.timeout:.0f}s; still down: {pending}",
              file=sys.stderr)
        return 1
    print("[wait_for] all services up")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

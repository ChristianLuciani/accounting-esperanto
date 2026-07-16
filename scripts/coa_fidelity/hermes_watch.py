#!/usr/bin/env python3
"""
Hermes watcher: detects when a verified jurisdiction's official chart-of-
accounts source may have changed, so the COA-fidelity sweep's "verified"
status doesn't silently go stale as countries revise their statutory charts
over time (rare, but it happens).

Deliberately does NOT re-map anything automatically. It only ever:
  1. checks whether the cited primary source's content looks different from
     what was hashed at verification time, and
  2. if so, downgrades that jurisdiction to fidelity_status:
     drift_detected_needs_review and opens a GitHub issue -- a human/session
     re-verifies from scratch via the normal sweep protocol
     (research/coa_fidelity/README.md).

Cheap-first: a conditional HTTP request (If-None-Match / If-Modified-Since)
is tried before any full refetch, so a quarterly run across dozens of
government sites costs almost nothing when nothing has changed.

Only jurisdictions with fidelity_status == "verified" are checked -- there is
nothing to compare a partial_curated_subset or not_started row against yet.

Usage:
    python3 scripts/coa_fidelity/hermes_watch.py \
        --status research/coa_fidelity/STATUS.yaml \
        [--repo ChristianLuciani/accounting-esperanto]  # for gh issue create
        [--dry-run]                                     # report only, no writes/issues
"""
import argparse
import hashlib
import subprocess
import sys
import tempfile
from datetime import date

import yaml

USER_AGENT = "Kontablo-Hermes-Watcher/1.0 (+https://github.com/ChristianLuciani/accounting-esperanto)"

# curl, not urllib/requests: several statutory-chart authorities (older
# government infrastructure) fail Python's default SSL/TLS negotiation
# (observed: SSLV3_ALERT_HANDSHAKE_FAILURE against Ecuador's Supercias site)
# while curl's system libcurl negotiates fine with default settings. Every
# jurisdiction's watcher fetch goes through curl for this reason -- one
# fetch mechanism, proven against the flakiest real source, rather than a
# urllib-first path that silently degrades on exactly the servers most
# likely to be old and unmaintained.
CURL_BASE = ["curl", "-sS", "-L", "--max-time", "60", "-A", USER_AGENT]


def _parse_headers(header_text):
    headers = {}
    for line in header_text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            headers[k.strip().lower()] = v.strip()
    return headers


def conditional_head(url, etag, last_modified):
    """Returns 'unchanged', 'changed', or 'unknown' (server gave us nothing
    to compare against, so we must fall back to a full fetch)."""
    cmd = CURL_BASE + ["-I", url]
    if etag:
        cmd += ["-H", f"If-None-Match: {etag}"]
    if last_modified:
        cmd += ["-H", f"If-Modified-Since: {last_modified}"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=True).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return "unknown", None, None

    # curl -L can print one header block per redirect hop; the final block
    # (after the last blank-line-separated section) is the one that matters.
    blocks = [b for b in out.split("\r\n\r\n") if b.strip()]
    headers = _parse_headers(blocks[-1]) if blocks else {}
    status_line = blocks[-1].splitlines()[0] if blocks else ""
    new_etag = headers.get("etag")
    new_lm = headers.get("last-modified")

    if "304" in status_line:
        return "unchanged", etag, last_modified
    if not new_etag and not new_lm:
        return "unknown", None, None
    if new_etag == etag and new_lm == last_modified:
        return "unchanged", new_etag, new_lm
    return "changed", new_etag, new_lm


def fetch_and_hash(url):
    """Full fetch + content hash. PDFs are text-extracted via pdftotext so a
    cosmetic re-render doesn't look like a content change; falls back to
    hashing raw bytes if pdftotext isn't available (flagged in the return)."""
    with tempfile.NamedTemporaryFile() as body_f:
        # -D - sends headers to stdout while -o diverts the body to a file,
        # so the two never interleave even for a binary (PDF) body.
        header_text = subprocess.run(
            CURL_BASE + ["-D", "-", "-o", body_f.name, url],
            capture_output=True, text=True, timeout=90, check=True,
        ).stdout
        blocks = [b for b in header_text.split("\r\n\r\n") if b.strip()]
        headers = _parse_headers(blocks[-1]) if blocks else {}
        etag = headers.get("etag")
        last_modified = headers.get("last-modified")
        body_f.seek(0)
        raw = body_f.read()

    is_pdf = raw[:4] == b"%PDF"
    if not is_pdf:
        digest = hashlib.sha256(raw).hexdigest()
        return digest, etag, last_modified, "raw_bytes"

    with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_f:
        pdf_f.write(raw)
        pdf_f.flush()
        try:
            text = subprocess.run(
                ["pdftotext", "-layout", pdf_f.name, "-"],
                capture_output=True, check=True, timeout=60,
            ).stdout
            digest = hashlib.sha256(text).hexdigest()
            return digest, etag, last_modified, "pdftotext_extracted"
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            digest = hashlib.sha256(raw).hexdigest()
            return digest, etag, last_modified, "raw_bytes_fallback_no_pdftotext"


def open_drift_issue(repo, row, old_hash, new_hash, extraction_mode):
    title = f"[Hermes] Possible chart-of-accounts change: {row['name']} ({row['iso']})"
    body = (
        f"The Hermes watcher detected that the content at the cited primary "
        f"source for **{row['name']}** ({row['iso']}) no longer matches what "
        f"was hashed when this jurisdiction was last verified.\n\n"
        f"- Source: {row.get('source_url')}\n"
        f"- Authority: {row.get('source_authority')}\n"
        f"- Last verified: {row.get('last_verified')}\n"
        f"- Previous hash: `{old_hash[:16]}...`\n"
        f"- New hash: `{new_hash[:16]}...`\n"
        f"- Extraction mode: {extraction_mode}\n\n"
        f"This does **not** mean the chart definitely changed -- a cosmetic "
        f"PDF re-render or a URL redirect can also change the hash. A human "
        f"or a fresh session should re-run the sweep protocol "
        f"(research/coa_fidelity/README.md) for this jurisdiction to confirm "
        f"and re-verify before trusting this again.\n\n"
        f"`research/coa_fidelity/STATUS.yaml` has been updated to "
        f"`fidelity_status: drift_detected_needs_review` for `{row['iso']}`."
    )
    cmd = ["gh", "issue", "create", "--title", title, "--body", body, "--label", "coa-fidelity"]
    if repo:
        cmd += ["--repo", repo]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"WARNING: could not open GitHub issue for {row['iso']}: {e}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="research/coa_fidelity/STATUS.yaml")
    ap.add_argument("--repo", default=None, help="owner/repo for `gh issue create`")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    doc = yaml.safe_load(open(args.status, encoding="utf-8"))
    today = date.today().isoformat()
    checked, drifted, baselined, errored = 0, 0, 0, 0

    for row in doc["jurisdictions"]:
        if row.get("fidelity_status") != "verified" or not row.get("source_url"):
            continue
        checked += 1
        url = row["source_url"]
        print(f"[{row['iso']}] checking {url}")

        status = "unknown"
        new_etag = new_lm = None
        if row.get("source_etag") or row.get("source_last_modified_header"):
            status, new_etag, new_lm = conditional_head(
                url, row.get("source_etag"), row.get("source_last_modified_header")
            )

        if status == "unchanged":
            print(f"  unchanged (conditional headers matched)")
            if not args.dry_run:
                row["source_etag"] = new_etag or row.get("source_etag")
                row["source_last_modified_header"] = new_lm or row.get("source_last_modified_header")
                row["last_checked"] = today
            continue

        try:
            new_hash, fetched_etag, fetched_lm, mode = fetch_and_hash(url)
        except Exception as e:
            print(f"  ERROR fetching: {e}", file=sys.stderr)
            errored += 1
            continue

        old_hash = row.get("source_content_hash")
        if old_hash is None:
            print(f"  no baseline yet -- establishing one (mode={mode})")
            baselined += 1
            if not args.dry_run:
                row["source_content_hash"] = new_hash
                row["source_etag"] = fetched_etag
                row["source_last_modified_header"] = fetched_lm
                row["last_checked"] = today
        elif old_hash == new_hash:
            print(f"  unchanged (content hash matches)")
            if not args.dry_run:
                row["source_etag"] = fetched_etag
                row["source_last_modified_header"] = fetched_lm
                row["last_checked"] = today
        else:
            print(f"  DRIFT DETECTED (mode={mode}) -- flagging for review")
            drifted += 1
            if not args.dry_run:
                row["fidelity_status"] = "drift_detected_needs_review"
                row["last_checked"] = today
                prior_note = row.get("notes") or ""
                row["notes"] = (
                    f"{prior_note} [{today}] Hermes watcher detected a content hash "
                    f"change at the primary source -- needs re-verification."
                ).strip()
                open_drift_issue(args.repo, row, old_hash, new_hash, mode)
                row["source_content_hash"] = new_hash
                row["source_etag"] = fetched_etag
                row["source_last_modified_header"] = fetched_lm

    print(f"\nChecked {checked} verified jurisdiction(s): "
          f"{baselined} baselined, {drifted} drift-flagged, {errored} errored.")

    if not args.dry_run:
        with open(args.status, "w", encoding="utf-8") as f:
            yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"Updated {args.status}")


if __name__ == "__main__":
    main()

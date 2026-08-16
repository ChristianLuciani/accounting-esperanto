"""Content-addressed snapshot fetcher for the round-2 real-data validation.

Round 2 scores Kontablo's resolver against public filings. Public registries are
living systems: they republish, correct, and withdraw filings. The synthetic
experiment guarantees byte-for-byte reproducibility with a pinned FX table
(``core/harness/fx.py``); this module is the equivalent guarantee for real data,
implementing the two-regime model of ``research/real_data_validation_plan.md`` §7.

Both regimes produce the same artifact — a committed ``manifest.json`` recording,
per file: source URL, SHA-256, byte size, retrieval timestamp, and license
regime. What differs is whether the *payload* may be redistributed:

``public_domain``   EDGAR (U.S. government work).
``open_data``       IMF, Eurostat, GLEIF — published for reuse under their own terms.
``no_redistribution`` UK Companies House — no explicit reuse license published, so
                    the payload is NEVER committed. The manifest names the exact
                    accession and its hash; a third party reproduces by
                    re-downloading and checking the hash.

Payloads land in ``research/real_data_snapshots/`` which is gitignored wholesale
(EDGAR quarters alone are ~66 MB compressed / ~1 GB extracted — vendoring them
would bloat the repo without adding evidentiary value the hash does not already
provide). What IS committed is the manifest plus the small derived artifacts each
experiment produces from it. Scoring therefore runs hermetically offline from
committed derivatives, exactly as the CI claims-evidence gate requires.

Set ``KONTABLO_REAL_DATA_OFFLINE=1`` to forbid all network access: cached files
are verified against the manifest and a missing file is an error rather than a
silent re-fetch. This is the mode the reproducibility check runs in.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SNAPSHOT_DIR = os.path.join(ROOT, "research", "real_data_snapshots")

# SEC requires a descriptive User-Agent with contact info and rate-limits to
# 10 req/s; the other sources are unauthenticated but we identify ourselves
# uniformly so operators can attribute the traffic.
USER_AGENT = os.environ.get(
    "KONTABLO_USER_AGENT",
    "Kontablo Research (accounting-esperanto) cluciani@gmail.com",
)

LICENSE_REGIMES = ("public_domain", "open_data", "no_redistribution")

_MIN_INTERVAL_S = 0.2  # be a good citizen; SEC caps at 10 req/s
_last_request = [0.0]


def offline() -> bool:
    return os.environ.get("KONTABLO_REAL_DATA_OFFLINE", "") == "1"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_path(experiment: str) -> str:
    return os.path.join(ROOT, "research", "experiments", experiment, "manifest.json")


def load_manifest(experiment: str) -> dict:
    path = manifest_path(experiment)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return {"experiment": experiment, "files": {}}


def save_manifest(experiment: str, manifest: dict) -> str:
    path = manifest_path(experiment)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Sort keys so re-running the downloader produces a stable diff.
    manifest["files"] = dict(sorted(manifest["files"].items()))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return path


def _throttle() -> None:
    delta = time.time() - _last_request[0]
    if delta < _MIN_INTERVAL_S:
        time.sleep(_MIN_INTERVAL_S - delta)
    _last_request[0] = time.time()


def _download(url: str, dest: str, timeout: int, retries: int) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            _throttle()
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                tmp = dest + ".part"
                with open(tmp, "wb") as fh:
                    while True:
                        chunk = resp.read(1 << 20)
                        if not chunk:
                            break
                        fh.write(chunk)
                os.replace(tmp, dest)
            return
        except urllib.error.HTTPError as exc:  # pragma: no cover - network
            last_error = exc
            # A 4xx other than rate-limiting is a permanent answer: the URL is
            # wrong or the resource is gone. Retrying just delays the real error.
            if 400 <= exc.code < 500 and exc.code != 429:
                raise RuntimeError(f"HTTP {exc.code} for {url}") from exc
            time.sleep(2 ** attempt)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:  # pragma: no cover - network
            last_error = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"download failed after {retries} attempts: {url}") from last_error


def fetch(
    url: str,
    experiment: str,
    key: str,
    license_regime: str,
    *,
    relpath: str | None = None,
    timeout: int = 180,
    retries: int = 3,
    note: str | None = None,
) -> str:
    """Fetch ``url`` into the snapshot dir, hash it, and record it in the manifest.

    Returns the local path. Idempotent: an already-present file whose SHA-256
    matches the manifest is never re-downloaded, so re-running a downloader is
    cheap and does not perturb the recorded retrieval date. A file present on
    disk whose hash does NOT match the manifest is a hard error — that is the
    upstream-republished case, and it must be adjudicated by a human rather than
    silently overwritten, because it would change every downstream number.
    """
    if license_regime not in LICENSE_REGIMES:
        raise ValueError(f"unknown license regime: {license_regime}")

    manifest = load_manifest(experiment)
    entry = manifest["files"].get(key)
    dest = os.path.join(SNAPSHOT_DIR, experiment, relpath or key)

    if os.path.exists(dest):
        digest = sha256_file(dest)
        if entry and entry.get("sha256") and entry["sha256"] != digest:
            raise RuntimeError(
                f"snapshot hash mismatch for {key}\n"
                f"  manifest: {entry['sha256']}\n"
                f"  on disk:  {digest}\n"
                "Upstream republished or the local copy is corrupt. Adjudicate "
                "manually — do not silently overwrite; every derived number depends on it."
            )
        if entry:
            return dest
    elif offline():
        raise RuntimeError(
            f"KONTABLO_REAL_DATA_OFFLINE=1 but snapshot is missing: {key} ({dest}). "
            "Re-run the downloader online to repopulate it."
        )
    else:
        _download(url, dest, timeout, retries)
        digest = sha256_file(dest)
        if entry and entry.get("sha256") and entry["sha256"] != digest:
            raise RuntimeError(
                f"downloaded {key} but its hash differs from the committed manifest\n"
                f"  manifest: {entry['sha256']}\n"
                f"  fetched:  {digest}\n"
                "Upstream has republished this file. Record the change as a dated "
                "addendum rather than silently rescoring against new data."
            )

    manifest["files"][key] = {
        "url": url,
        "sha256": digest,
        "bytes": os.path.getsize(dest),
        "retrieved_utc": (entry or {}).get(
            "retrieved_utc", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ),
        "license_regime": license_regime,
        "local_path": os.path.relpath(dest, ROOT),
        **({"note": note} if note else {}),
    }
    save_manifest(experiment, manifest)
    return dest


def verify(experiment: str) -> list[str]:
    """Re-hash every manifested file. Returns a list of human-readable problems."""
    manifest = load_manifest(experiment)
    problems = []
    for key, entry in manifest["files"].items():
        path = os.path.join(ROOT, entry["local_path"])
        if not os.path.exists(path):
            problems.append(f"{key}: missing ({entry['local_path']})")
            continue
        digest = sha256_file(path)
        if digest != entry["sha256"]:
            problems.append(f"{key}: hash mismatch (expected {entry['sha256']}, got {digest})")
    return problems


if __name__ == "__main__":  # pragma: no cover - operator convenience
    import sys

    for exp in sys.argv[1:] or ["tag_resolution_v1", "public_sector_gfs_v1", "consolidation_v3_real"]:
        issues = verify(exp)
        print(f"{exp}: {'OK' if not issues else chr(10).join(issues)}")

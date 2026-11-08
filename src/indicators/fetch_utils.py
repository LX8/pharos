#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared, resilient fetch helpers for the open indicators — one place, one behavior.

Both indicator pipelines (WGI governance, voice-divergence) talk to flaky public
endpoints (the World Bank API returns transient 400s; Our World in Data is reliable
but the network is not). Before this module each had its own retry loop — and they
disagreed: `wgi_governance._get` slept `1.0 + i` between tries, while
`voice_divergence._fetch_csv` slept **nothing at all** (it retried instantly, which
is useless against a rate-limit window). This consolidates them into one helper with
**exponential backoff + jitter**, so retries spread off a shared rate-limit window
instead of hammering the same second.

The jitter uses `random` only for retry *timing* — it never touches the data, so
pipeline outputs stay fully deterministic.

Stdlib only.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import time
import urllib.request

DEFAULT_UA = "Mozilla/5.0 (compatible; pharos-open-indicators/1.0)"


def _backoff_sleep(i, base_delay):
    """Exponential backoff with jitter: base*2^i + U(0, base). O(1)."""
    time.sleep(base_delay * (2 ** i) + random.uniform(0.0, base_delay))


def fetch_bytes(url, *, attempts=4, timeout=90, base_delay=1.0, ua=DEFAULT_UA):
    """GET raw bytes with retry. Raises RuntimeError naming the URL after the last try."""
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 — transient HTTP 400 / timeout / reset; retry then surface
            last = e
            if i < attempts - 1:
                _backoff_sleep(i, base_delay)
    raise RuntimeError(f"failed to fetch {url} after {attempts} attempts: {last}")


def fetch_text(url, **kw):
    return fetch_bytes(url, **kw).decode("utf-8")


def fetch_json(url, **kw):
    """GET + parse JSON."""
    return json.loads(fetch_text(url, **kw))


def fetch_csv_rows(url, **kw):
    """GET + parse CSV into a list of dict rows (RFC-4180 via csv.DictReader)."""
    return list(csv.DictReader(io.StringIO(fetch_text(url, **kw))))


def sha256_text(s):
    """Content hash of a UTF-8 string, prefixed `sha256:` — for input provenance."""
    return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(path):
    """Content hash of a file's bytes, prefixed `sha256:` — deterministic across
    platforms/encodings, unlike hashing a decoded string. For input provenance."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def file_provenance(path, source_url, fetched_utc):
    """Return the provenance block the DATA_CONTRACT promises each derived JSON
    companion carries: the input snapshot's sha256, its source URL, and the time it
    was fetched. Reads the actual committed bytes (so a swapped/edited upstream
    snapshot is detectable from the derived file alone), and never calls now() —
    the timestamp is the snapshot's own fetch time, so offline mode stays deterministic.

    All three fields come from the *pinned input* (the snapshot), not from the live
    fetch: a derived file's provenance describes how its inputs were obtained, which
    is fixed at pin time, not at compute time.
    """
    return {"source_url": source_url, "fetched_utc": fetched_utc,
            "input_sha256": sha256_file(path)}

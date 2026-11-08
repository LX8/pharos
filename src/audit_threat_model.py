#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Threat-model data gate — "watch power, not people", enforced on the published data.

[`THREAT_MODEL.md`](../THREAT_MODEL.md) §4.3 sets a hard floor: every published output is
**country / institution level**, never sub-national, geolocated, or person-level — the spatial
floor that keeps an open dataset from becoming a targeting tool (the predictive-policing failure
mode). That floor was documented but nothing machine-checked it. This audit scans every committed
data file (`data/derived/*`, `data/snapshots/*`) and FAILS the build if any column name or JSON key
names a resolution below country level.

Matching is **token**-based (split on non-alphanumerics), in three layers so it catches real-world
spellings without false-positiving the legitimate country-level columns this repo ships:

1. **atomic denylist** — unambiguous sub-national / person tokens (`city`, `district`, `geoid`,
   `birth`, `admin`, …); `latest` != `lat`, `average` != `age`, so no substring false-positives.
2. **token regexes** — arbitrary admin levels and indexed statistical geographies
   (`adm3`, `admin5`, `nuts2`).
3. **qualifier→suffix adjacency** — snake_case fields whose tokens are individually innocuous but
   jointly person/sub-national: `first_name`, `national_id`, `state_code`. `country_name` and
   `dimension_name` stay clean because `country`/`dimension` are not qualifiers, and `state_capacity`
   stays clean because `capacity` is not a locational suffix.

It also scans the **values** of long/tidy-format label columns (a `variable` column whose rows say
`latitude` would otherwise smuggle the leak past a header-only check).

**Documented limits** (so a reviewer never mistakes a green run for a proof): it checks *names* and
long-format *label values*, not arbitrary cell values or JSON string leaves; and genuinely ambiguous
bare columns (`region`/`state` alone — which may mean a *coarser* continent grouping or a *finer*
province) are only flagged when carrying a locational suffix, so a bare one still needs the human
§4.3 review. Pure core (`forbidden_in`) + thin CLI. Stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

# 1. Atomic forbidden tokens — each unambiguously names a sub-country or person-level resolution.
FORBIDDEN_TOKENS = {
    # geolocation / coordinates — incl. ENCODED point formats (geohash, Open Location Code,
    # tile/quad keys, what3words), which resolve to point precision without 'lat'/'lon' names;
    # a bare "utm"/"h3" token is deliberately excluded (too collision-prone: utm_source, h3 headers)
    "lat", "latitude", "lon", "lng", "longitude", "coord", "coords", "coordinate",
    "coordinates", "geometry", "gps", "easting", "northing", "geocode", "geoid", "fips",
    "geohash", "pluscode", "plus_code", "olc", "quadkey", "tilekey", "mgrs",
    "what3words", "w3w", "geopoint", "latlng", "latlon",
    # sub-national administrative units (unambiguous spellings)
    "admin", "district", "subdistrict", "province", "municipality", "municipal", "county",
    "ward", "precinct", "subnational", "locality", "neighborhood", "neighbourhood",
    "constituency", "subregion", "city", "town", "village", "hamlet", "settlement",
    "commune", "canton", "prefecture", "oblast", "raion", "parish", "borough", "township",
    "barangay", "woreda", "upazila", "tehsil", "metro", "metropolitan", "gadm", "priogrid", "gid",
    # statistical-geography / census codes
    "postal", "postcode", "zip", "zipcode", "tract", "censustract", "blockgroup", "cbsa",
    "msa", "lsoa", "msoa",
    # person-level
    "person", "individual", "respondent", "firstname", "lastname", "surname", "fullname",
    "forename", "dob", "birth", "birthdate", "birthplace", "phone", "telephone", "mobile",
    "email", "ssn", "passport", "household", "address", "ipaddress", "age", "gender", "sex",
    "ethnicity", "religion", "occupation", "salary", "income", "biometric", "fingerprint",
    "disability", "caste",
    # national person-ID schemes (a column of these is person-level by definition)
    "aadhaar", "cpf", "curp", "cnic", "nino", "pesel", "dni", "nric", "bsn", "taxid", "tin",
}

# 2. Token regexes — arbitrary admin levels and indexed statistical geographies.
FORBIDDEN_PATTERNS = (
    re.compile(r"^adm\d+$"),     # GADM / HDX admin levels: adm1 .. adm5
    re.compile(r"^admin\d+$"),   # admin1 .. admin5 (concatenated)
    re.compile(r"^nuts\d*$"),    # EU NUTS regions: nuts, nuts1 .. nuts3
    re.compile(r"^gid\d+$"),     # GADM GID_1.. concatenated forms
)

# 3. Adjacency: a qualifier token immediately followed by a suffix token resolves to a finer-than-
# country or person field even though each token alone is innocuous. Tuned so `country_name` /
# `dimension_name` / `state_capacity` never match.
_NAME_QUALIFIERS = {"first", "last", "given", "family", "middle", "maiden", "sur", "nick",
                    "fore", "full", "legal", "real", "mother", "father", "spouse"}
_GEO_QUALIFIERS = {"region", "state", "department", "division", "zone", "place", "site", "geo", "adm",
                   "plus", "grid", "tile"}  # plus_code / grid_code / tile_id — encoded point formats
_ID_QUALIFIERS = {"national", "voter", "patient", "tax", "passport", "social", "personal",
                  "resident", "citizen", "beneficiary", "member", "user", "employee", "student"}
_NAME_SUFFIX = {"name", "names"}
_GEO_SUFFIX = {"name", "names", "code", "id", "fips", "geoid", "level", "boundary"}
_ID_SUFFIX = {"id", "ids", "number", "no", "num", "uid", "uuid"}

_SPLIT = re.compile(r"[^a-z0-9]+")


def _name_problem(name):
    """Pure. Return the offending reason for one column/key name, or None. O(tokens)."""
    toks = [t for t in _SPLIT.split(str(name).lower()) if t]
    for i, t in enumerate(toks):
        if t in FORBIDDEN_TOKENS:
            return t
        if any(p.match(t) for p in FORBIDDEN_PATTERNS):
            return t
        if i + 1 < len(toks):
            nxt = toks[i + 1]
            if (t in _NAME_QUALIFIERS and nxt in _NAME_SUFFIX) \
                    or (t in _ID_QUALIFIERS and nxt in _ID_SUFFIX) \
                    or (t in _GEO_QUALIFIERS and nxt in _GEO_SUFFIX):
                return f"{t}_{nxt}"
    return None


# Long/tidy-format columns whose *values* label what each row measures — scanned so a
# `variable`/`indicator` column with a row value of `latitude` can't slip past a header-only check.
LONG_LABEL_COLUMNS = {"variable", "indicator", "metric", "measure", "series", "dimension",
                      "level", "geo_level", "geolevel", "unit", "category", "type",
                      "attribute", "field", "parameter"}


def forbidden_in(names):
    """Pure. Return [(name, reason)] for any name that resolves below country level. O(names)."""
    out = []
    for name in names:
        r = _name_problem(name)
        if r is not None:
            out.append((name, r))
    return out


def _json_keys(obj):
    """Every dict key appearing anywhere in a JSON structure (iterative; handles big files)."""
    keys, stack = set(), [obj]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            keys.update(x.keys())
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x)
    return keys


def scan_file(path):
    """Return [(column-or-key, reason)] for one data file (csv header + label values, or json keys)."""
    if path.endswith(".csv"):
        with open(path, encoding="utf-8") as f:
            rows = list(csv.reader(f))
        if not rows:
            return []
        header = rows[0]
        problems = list(forbidden_in(header))
        # long/tidy format: scan the distinct values of any label column too.
        for i, h in enumerate(header):
            if h.strip().lower() in LONG_LABEL_COLUMNS:
                vals = sorted({r[i] for r in rows[1:] if i < len(r)})
                problems += [(f"{h}={v}", tok) for v, tok in forbidden_in(vals)]
        return problems
    if path.endswith(".json"):
        with open(path, encoding="utf-8") as f:
            try:
                obj = json.load(f)
            except json.JSONDecodeError:
                return []   # malformed JSON is another gate's job
        return forbidden_in(_json_keys(obj))
    return []


def _data_files(repo):
    out = []
    for sub in ("data/derived", "data/snapshots"):
        d = os.path.join(repo, sub)
        if os.path.isdir(d):
            out += [os.path.join(d, f) for f in sorted(os.listdir(d))
                    if f.endswith((".csv", ".json"))]
    return out


def _default_repo():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Watch power, not people: fail if any published data file drops below country level.")
    ap.add_argument("--repo", default=_default_repo())
    args = ap.parse_args(argv)

    files = _data_files(args.repo)
    if not files:
        # A gate that scans nothing certifies nothing — fail loudly instead of vacuously passing.
        print("threat-model data gate — 0 files found under data/derived / data/snapshots")
        print("FAIL: nothing to scan — wrong --repo, or the data directories are missing.")
        return 1
    violations = []
    for path in files:
        for name, tok in scan_file(path):
            violations.append((os.path.relpath(path, args.repo), name, tok))

    print(f"threat-model data gate — {len(files)} files, {len(violations)} violation(s)")
    for rel, name, tok in violations:
        print(f"  ✗ {rel}: column/key '{name}' looks sub-national / person-level ('{tok}')")
    if violations:
        print("FAIL: a published data file drops below country/institution level (THREAT_MODEL.md §4.3). "
              "Watch power, not people — coarsen or remove it.")
        return 1
    # A green name/label scan is NOT a proof. The gate checks column/key *names* and
    # long-format *label values* only — it does not inspect arbitrary cell values or
    # JSON string leaves, and a bare `region`/`state` column passes (it may mean a
    # coarser grouping or a finer province). State this on every green run so a clean
    # build is never mistaken for clearance of the human §4.3 mosaic/small-cell review.
    print("threat-model: ok — all published data is country/institution level")
    print("  NOTE: name/label scan only — cell values and JSON string leaves are NOT checked,")
    print("        and bare region/state columns pass; the THREAT_MODEL.md §4.3 human review")
    print("        (mosaic + small-cell) is still required. A green run is not a proof.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

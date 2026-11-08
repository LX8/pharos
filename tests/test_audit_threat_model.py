# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for the threat-model data gate.

The earlier version of this suite only exercised tokens that were already on the denylist, so a
green run could not prove coverage — a too-narrow list passed silently. These tests instead pin
both directions with a corpus the way a real dataset would spell things: a `MUST_FLAG` list of
sub-national / geolocated / person-level columns that every one must trip, and a `MUST_PASS` list
of legitimate country-level columns (including the ambiguous-but-fine `state_capacity`,
`urban_population`, `country_name`) that none may trip. Adding a new spelling is one line, and a
denylist that regresses (too narrow OR too broad) fails immediately.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import audit_threat_model as a  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

# Real-world column/key names that name a resolution BELOW country level — each MUST be flagged.
MUST_FLAG = [
    # geolocation
    "lat", "latitude", "lon", "lng", "longitude", "x_coord", "y_coordinate", "gps", "geoid", "fips",
    # admin units, common spellings + arbitrary levels
    "district", "subdistrict", "province", "county", "city", "town", "village", "settlement",
    "commune", "canton", "prefecture", "oblast", "parish", "borough", "township", "barangay",
    "admin", "admin1", "admin2", "admin3", "admin5", "adm3", "adm_level", "admin_level",
    "nuts", "nuts2", "nuts3", "gadm", "census_tract", "blockgroup", "msoa", "priogrid",
    # ambiguous geo qualifiers carrying a locational suffix
    "region_name", "region_code", "state_name", "state_code", "department_id", "geo_level",
    # person-level, including the snake_case spellings the old list missed
    "person", "individual", "respondent", "first_name", "last_name", "full_name", "given_name",
    "family_name", "middle_name", "maiden_name", "surname", "date_of_birth", "birth_date",
    "birthplace", "national_id", "voter_id", "patient_id", "passport", "household", "home_address",
    "email", "phone_number", "occupation", "salary", "ethnicity", "religion", "biometric",
    # encoded point-geolocation formats (R7 review: point precision without 'lat'/'lon' names)
    "geohash", "plus_code", "pluscode", "quadkey", "mgrs", "what3words", "w3w_address",
    "geopoint", "latlng",
    # national person-ID schemes
    "aadhaar", "cpf", "curp", "cnic", "nino", "pesel", "nric", "bsn", "tax_id",
]

# Legitimate country-level columns/keys this project ships or plausibly would — none may be flagged.
MUST_PASS = [
    "iso3", "code", "country", "country_name", "country_code", "dimension", "dimension_name",
    "year", "year_base", "year_latest", "sc_base", "sc_latest", "lb_base", "ub_base", "change",
    "se_diff", "z", "p_two_sided", "verdict", "model", "crps", "crps_skill", "brier", "value",
    "label", "evidence_strength", "flag_basis_mix", "wgi_va_direction", "no_change", "climatology",
    # ambiguous-but-fine: poli-sci uses "state"/"region" to mean the country or a continent grouping
    "state_capacity", "state_fragility", "statehood", "regional_mean", "subregional_total",
    "urban_population", "rural_share", "nationality_law", "average", "coverage", "language",
    "page", "related", "message", "personnel", "name", "time_zone", "valid_id",
]


class TestCoverage(unittest.TestCase):
    def test_every_subnational_or_person_column_is_flagged(self):
        missed = [c for c in MUST_FLAG if not a.forbidden_in([c])]
        self.assertEqual(missed, [], f"these below-country columns slipped past the gate: {missed}")

    def test_no_legitimate_country_column_is_flagged(self):
        wrong = [(c, a.forbidden_in([c])[0][1]) for c in MUST_PASS if a.forbidden_in([c])]
        self.assertEqual(wrong, [], f"these legitimate country-level columns were false-positived: {wrong}")

    def test_reason_is_the_offending_token(self):
        self.assertEqual(a.forbidden_in(["district_code"]), [("district_code", "district")])
        self.assertEqual(a.forbidden_in(["admin3"]), [("admin3", "admin3")])
        self.assertEqual(a.forbidden_in(["first_name"]), [("first_name", "first_name")])


class TestJsonWalk(unittest.TestCase):
    def test_json_keys_walk_is_recursive(self):
        obj = {"countries": {"USA": {"value": 1}}, "rows": [{"latitude": 2}]}
        self.assertIn("latitude", a._json_keys(obj))
        self.assertEqual([tok for _, tok in a.forbidden_in(a._json_keys(obj))], ["latitude"])


class TestScanFileBites(unittest.TestCase):
    def _csv(self, body):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "f.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        return path

    def test_header_leak_fails(self):
        toks = {t for _, t in a.scan_file(self._csv("iso3,latitude,longitude,value\nUSA,38.9,-77.0,1\n"))}
        self.assertTrue({"latitude", "longitude"} <= toks, toks)

    def test_long_format_value_leak_fails(self):
        # tidy/long format: a forbidden token hiding in a label column's VALUES, not the header.
        viol = a.scan_file(self._csv("iso3,variable,value\nUSA,latitude,38.9\nUSA,gdp,21000\n"))
        self.assertTrue(any(tok == "latitude" for _, tok in viol), viol)

    def test_clean_csv_passes(self):
        self.assertEqual(
            a.scan_file(self._csv("iso3,country_name,year_latest,value\nUSA,United States,2024,1\n")), [])


class TestVacuousPassGuard(unittest.TestCase):
    def test_zero_files_fails_the_gate(self):
        # a gate that scans nothing certifies nothing — wrong --repo must FAIL, not pass GREEN
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(a.main(["--repo", d]), 1)


class TestShippedData(unittest.TestCase):
    """Every committed data file is country/institution level — the covenant, enforced."""

    def test_all_published_data_passes(self):
        violations = []
        for path in a._data_files(REPO):
            violations += [(os.path.basename(path), n, t) for n, t in a.scan_file(path)]
        self.assertEqual(violations, [], f"sub-national/person-level column shipped: {violations}")


if __name__ == "__main__":
    unittest.main()

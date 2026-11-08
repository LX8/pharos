# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for the input-drift check's pure core.

Only the comparison logic is tested here — the live fetch in `main()` is network-bound and out of
scope for the offline gate. Pins the two properties that matter: the volatile provenance stamps are
ignored (an offline vs live run of the *same* data must NOT read as drift), and a real change to a
computed number IS caught.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import drift_check as d  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


class TestSubstantive(unittest.TestCase):
    def test_strips_volatile_keys_recursively(self):
        obj = {"mode": "offline-snapshot", "fetched_utc": "2026-06-18T00:00:00+00:00",
               "overall": {"within_noise": 1080, "mode": "x"}, "rows": [{"v": 1, "mode": "y"}]}
        got = d.substantive(json.dumps(obj), "x.json")
        self.assertEqual(got, {"overall": {"within_noise": 1080}, "rows": [{"v": 1}]})

    def test_csv_is_verbatim(self):
        self.assertEqual(d.substantive("iso3,value\nUSA,1\n", "x.csv"), "iso3,value\nUSA,1\n")


class TestDiff(unittest.TestCase):
    def test_only_stamps_differ_is_not_drift(self):
        # the exact case the live check must not false-positive on: same numbers, live vs offline stamp
        committed = {"s.json": json.dumps({"mode": "offline-snapshot", "fetched_utc": "2026-06-18", "n": 88})}
        fresh = {"s.json": json.dumps({"mode": "live", "fetched_utc": "2026-07-04", "n": 88})}
        self.assertEqual(d.diff_derived(committed, fresh), [])

    def test_changed_number_is_drift(self):
        committed = {"s.json": json.dumps({"mode": "offline-snapshot", "n": 88})}
        fresh = {"s.json": json.dumps({"mode": "live", "n": 89})}
        self.assertEqual(d.diff_derived(committed, fresh), ["s.json"])

    def test_changed_csv_row_is_drift(self):
        self.assertEqual(d.diff_derived({"a.csv": "x,1\n"}, {"a.csv": "x,2\n"}), ["a.csv"])


class TestByteExactRestore(unittest.TestCase):
    """The pin restore MUST be byte-exact. The derived CSVs use CRLF; a text-mode round-trip
    silently strips the \\r and corrupts the committed data — the bug this pins against."""

    def test_helpers_preserve_crlf(self):
        orig = d.DERIVED
        try:
            with tempfile.TemporaryDirectory() as td:
                d.DERIVED = td
                d._write_bytes("x.csv", b"a,b\r\nc,d\r\n")
                self.assertEqual(d._read_bytes("x.csv"), b"a,b\r\nc,d\r\n")
        finally:
            d.DERIVED = orig

    def test_at_least_one_committed_csv_uses_crlf(self):
        # if this ever becomes false the risk is gone, but the guard should still hold
        raws = [open(os.path.join(REPO, "data", "derived", n), "rb").read()
                for n in d.DERIVED_FILES if n.endswith(".csv")]
        self.assertTrue(any(b"\r\n" in r for r in raws), "expected CRLF in a derived CSV")


class TestMainRobustness(unittest.TestCase):
    def test_missing_derived_file_is_a_clean_error(self):
        # a missing pin must give an actionable message + non-zero code, not a raw traceback
        orig = d.DERIVED
        try:
            with tempfile.TemporaryDirectory() as td:
                d.DERIVED = td
                self.assertEqual(d.main([]), 2)
        finally:
            d.DERIVED = orig

    def test_children_are_forced_live(self):
        # the whole point: children must run with SAA_OFFLINE=0, or an ambient offline env would make
        # them recompute from the snapshot and report a false "current" without ever fetching live.
        seen = []

        class _Done:
            returncode, stdout, stderr = 0, "", ""

        def _fake_run(cmd, **kw):
            seen.append(kw.get("env") or {})
            return _Done()

        orig, orig_note, orig_derived = d.subprocess.run, d._new_year_note, d.DERIVED
        try:
            with tempfile.TemporaryDirectory() as td:
                for name in d.DERIVED_FILES:        # work on a copy; never rewrite the committed pin
                    shutil.copyfile(os.path.join(orig_derived, name), os.path.join(td, name))
                d.DERIVED = td
                d.subprocess.run = _fake_run
                d._new_year_note = lambda: None     # the live V-Dem probe must never run in the offline suite
                code = d.main([])                   # fake subprocess writes nothing → fresh == pin → ok
                self.assertEqual(code, 0)
                self.assertTrue(seen, "subprocess.run was never called")
                self.assertEqual(seen[0].get("SAA_OFFLINE"), "0")
        finally:
            d.subprocess.run, d._new_year_note, d.DERIVED = orig, orig_note, orig_derived


class TestCommittedDerivedParses(unittest.TestCase):
    """Guards that every file the drift check will compare is present and substantive()-able."""

    def test_all_derived_files_readable(self):
        for name in d.DERIVED_FILES:
            path = os.path.join(REPO, "data", "derived", name)
            self.assertTrue(os.path.exists(path), f"missing derived file {name}")
            with open(path, encoding="utf-8") as f:
                d.substantive(f.read(), name)  # must not raise


if __name__ == "__main__":
    unittest.main()

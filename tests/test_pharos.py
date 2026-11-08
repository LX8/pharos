# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for the `pharos` CLI — each subcommand runs and prints the verified data.

The CLI reads the committed source of truth (ledger frontmatter + data/derived), so these also
guard that every subcommand stays wired to real data and exits cleanly. `verify` is not exercised
here (it just delegates to the already-tested dashboard and would re-run the whole suite)."""
import io
import contextlib
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pharos  # noqa: E402


def run(argv):
    """Run a pharos command, returning (exit_code, stdout)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = pharos.main(argv)
    return code, buf.getvalue()


class TestBriefAndReport(unittest.TestCase):
    def test_brief_prints_and_strips_header(self):
        code, out = run(["brief"])
        self.assertEqual(code, 0)
        self.assertIn("Pharos Brief", out)
        self.assertNotIn("<!--", out)                         # HTML/SPDX header stripped
        self.assertNotIn("SPDX", out)
        self.assertIn("noise", out.split("The ledger")[0])    # noise floor still leads

    def test_report_prints_watch_list(self):
        code, out = run(["report"])
        self.assertEqual(code, 0)
        self.assertIn("Watch List", out)
        self.assertNotIn("<!--", out)

    def test_missing_doc_is_a_clean_error(self):
        # if the generated doc isn't present, point at the make target — no traceback, non-zero exit
        orig = pharos.ROOT
        try:
            pharos.ROOT = os.path.join(orig, "no-such-root")
            code, out = run(["brief"])
            self.assertEqual(code, 1)
            self.assertIn("make brief", out)
        finally:
            pharos.ROOT = orig


class TestStripHtmlComments(unittest.TestCase):
    def test_strips_multiple_leading_comment_blocks(self):
        self.assertEqual(pharos._strip_html_comments("<!-- spdx --><!-- gen -->\n# Title"), "# Title")

    def test_no_comment_is_untouched(self):
        self.assertEqual(pharos._strip_html_comments("# Title\nbody"), "# Title\nbody")

    def test_unterminated_comment_does_not_hang(self):
        # a comment with no closing --> must break the loop, not spin forever
        self.assertEqual(pharos._strip_html_comments("<!-- oops\n# Title"), "<!-- oops\n# Title")


class TestLedger(unittest.TestCase):
    def test_lists_all_entries(self):
        code, out = run(["ledger"])
        self.assertEqual(code, 0)
        self.assertIn("41 of 41 graded entries", out)
        self.assertIn("SAA-001", out)

    def test_grade_filter(self):
        _, out = run(["ledger", "--grade", "REFUTED"])
        self.assertIn("1 of 41", out)        # exactly one REFUTED entry
        self.assertIn("SAA-011", out)

    def test_search_filter(self):
        _, out = run(["ledger", "--search", "inequality"])
        self.assertIn("SAA-033", out)

    def test_grade_filter_is_case_insensitive(self):
        _, out = run(["ledger", "--grade", "refuted"])
        self.assertIn("SAA-011", out)

    def test_bogus_grade_is_a_usage_error(self):
        # a typo must NOT be indistinguishable from a real empty result
        with self.assertRaises(SystemExit) as cm:
            run(["ledger", "--grade", "BOGUS"])
        self.assertEqual(cm.exception.code, 2)

    def test_zero_match_hint(self):
        _, out = run(["ledger", "--domain", "no-such-domain"])
        self.assertIn("no matches", out)

    def test_json_output(self):
        import json as _json
        code, out = run(["ledger", "--grade", "REFUTED", "--json"])
        self.assertEqual(code, 0)
        data = _json.loads(out)
        self.assertEqual([e["id"] for e in data], ["SAA-011"])


class TestShow(unittest.TestCase):
    def test_show_existing(self):
        code, out = run(["show", "SAA-031"])
        self.assertEqual(code, 0)
        self.assertIn("falsification_trigger", out)

    def test_show_missing_returns_1(self):
        code, out = run(["show", "SAA-999"])
        self.assertEqual(code, 1)

    def test_show_accepts_bare_number(self):
        code, out = run(["show", "31"])
        self.assertEqual(code, 0)
        self.assertIn("SAA-031", out)


class TestViews(unittest.TestCase):
    def test_watch_lists_triggers(self):
        code, out = run(["watch"])
        self.assertEqual(code, 0)
        self.assertIn("Falsification watch", out)
        self.assertEqual(out.count("↳"), 41)        # one trigger per entry

    def test_coverage_by_domain(self):
        code, out = run(["coverage"])
        self.assertEqual(code, 0)
        self.assertIn("political-economy", out)

    def test_indicators_headline(self):
        code, out = run(["indicators"])
        self.assertEqual(code, 0)
        self.assertIn("88% within measurement noise", out)

    def test_divergence_tally(self):
        code, out = run(["divergence"])
        self.assertEqual(code, 0)
        self.assertIn("CONCUR-DECLINE", out)

    def test_forecast_result(self):
        code, out = run(["forecast"])
        self.assertEqual(code, 0)
        self.assertIn("2600 pre-registered forecasts", out)
        self.assertIn("no_change", out)


class TestStaleAndStats(unittest.TestCase):
    def test_stats_is_all_derived(self):
        code, out = run(["stats"])
        self.assertEqual(code, 0)
        self.assertIn("41 graded entries", out)
        self.assertIn("7 validated mechanisms", out)

    def test_stale_future_date_flags_all(self):
        # a far-future "today" puts every entry past its review interval
        code, out = run(["stale", "--today", "2030-01-01"])
        self.assertEqual(code, 0)
        self.assertIn("41 stale of 41", out)

    def test_stale_recent_date_none_due(self):
        # at the date the entries were last reviewed, nothing is stale or due soon
        code, out = run(["stale", "--today", "2026-06-28"])
        self.assertEqual(code, 0)
        self.assertIn("0 stale of 41", out)

    def test_stale_malformed_date_is_a_usage_error(self):
        with self.assertRaises(SystemExit) as cm:
            run(["stale", "--today", "not-a-date"])
        self.assertEqual(cm.exception.code, 2)


class TestNoArgs(unittest.TestCase):
    def test_help_is_default(self):
        code, out = run([])
        self.assertEqual(code, 0)
        self.assertIn("pharos", out)


if __name__ == "__main__":
    unittest.main()

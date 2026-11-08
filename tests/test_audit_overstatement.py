# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for the overstatement audit — and a guard that the real graded
prose stays free of unconditional-certainty language."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import audit_overstatement as a  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


class TestScan(unittest.TestCase):
    def sev(self, text):
        return [f[0] for f in a.scan_text(text, "x.md")]

    def test_clean_prose_passes(self):
        self.assertEqual(a.scan_text("The evidence is contested; we grade it CONTESTED.", "x.md"), [])

    def test_serious_words_flagged(self):
        self.assertIn("SERIOUS", self.sev("This is definitively the case."))
        self.assertIn("SERIOUS", self.sev("It is beyond doubt."))
        self.assertIn("SERIOUS", self.sev("This is mathematically proven."))

    def test_quote_is_exempt(self):
        self.assertEqual(self.sev('The author wrote "definitively proven" back in 2020.'), [])

    def test_impossible_conditional_exempt_but_bare_flagged(self):
        self.assertEqual(self.sev("Levelling is impossible without a coalition."), [])
        self.assertIn("SERIOUS", self.sev("This outcome is impossible to fake."))

    def test_medium_is_non_fatal(self):
        self.assertEqual(self.sev("This is obviously the case."), ["MEDIUM"])

    def test_frontmatter_skipped(self):
        txt = "---\ntitle: definitively the strongest\n---\n\nThe body is clean."
        self.assertEqual(a.scan_text(txt, "x.md"), [])

    def test_url_line_exempt(self):
        self.assertEqual(self.sev("See https://x.org which says it is definitively proven."), [])

    def test_claim_bearing_bullet_is_scanned(self):
        # a `- ` bullet is NOT blanket-exempt — claim-bearing prose must be scanned
        self.assertIn("SERIOUS", self.sev("- This is definitively the case."))

    def test_citation_bullet_with_url_still_exempt(self):
        # a source bullet carries a URL, so it stays exempt via the URL rule
        self.assertEqual(self.sev("- Smith, J. (2020). Definitively proven. https://doi.org/x"), [])


class TestHtmlStripping(unittest.TestCase):
    """The public site is HTML; its prose (not its markup) must be scannable."""

    def test_tags_and_attrs_are_not_prose(self):
        # an alt= or class= attribute must never register as an overclaim
        html = '<img alt="definitively proven" class="hero"> <p>clean body</p>'
        self.assertEqual(a.scan_text(a._strip_html(html), "site/x.html"), [])

    def test_script_and_style_dropped(self):
        html = '<script>var x = "beyond doubt";</script><style>*{content:"mathematically proven"}</style>'
        self.assertEqual(a.scan_text(a._strip_html(html), "site/x.html"), [])

    def test_visible_prose_is_caught_through_html(self):
        html = '<p>This is <strong>definitively</strong> the strongest claim.</p>'
        self.assertIn("SERIOUS", [f[0] for f in a.scan_text(a._strip_html(html), "site/x.html")])

    def test_entities_decoded(self):
        html = '<p>beyond&nbsp;doubt</p>'
        self.assertIn("SERIOUS", [f[0] for f in a.scan_text(a._strip_html(html), "site/x.html")])


class TestCorpus(unittest.TestCase):
    """The shipped graded prose — ledger, article, REPORT, and the public site —
    must carry zero SERIOUS overstatements."""

    def test_corpus_has_zero_serious(self):
        serious = []
        for p in a._scope(REPO):
            with open(p, encoding="utf-8") as f:
                raw = f.read()
            text = a._strip_html(raw) if p.endswith(".html") else raw
            serious += [x for x in a.scan_text(text, os.path.relpath(p, REPO), a._lang_of(p))
                        if x[0] == "SERIOUS"]
        self.assertEqual(serious, [], f"overstatement in graded prose: {serious}")

    def test_site_is_in_scope(self):
        # guard against a future regression that silently drops the site from the audit
        scoped = [os.path.basename(p) for p in a._scope(REPO) if "site" in p]
        self.assertTrue(scoped, "site/index.html must be in the overstatement audit scope")

    def test_every_translated_page_is_scanned_in_its_language(self):
        # a language added to the site without its own patterns would be scanned in English only
        import build_site
        scoped = {os.path.relpath(p, REPO): a._lang_of(p) for p in a._scope(REPO)}
        for code, *_rest, rel in build_site.LANGS:
            self.assertEqual(scoped.get(os.path.join("site", rel)), code,
                             f"site/{rel} must be in scope and scanned as '{code}'")


class TestTranslationPatterns(unittest.TestCase):
    """The same honesty discipline in Spanish, German and Portuguese."""

    def sev(self, text, lang):
        return [f[0] for f in a.scan_text(text, "x.html", lang)]

    def test_overclaims_flagged_in_each_language(self):
        for lang, text in (("es", "El efecto es irrefutable."),
                           ("es", "Está demostrado más allá de toda duda."),
                           ("de", "Das ist zweifelsfrei bewiesen."),
                           ("de", "Der Befund ist mathematisch bewiesen."),
                           ("pt", "Isso foi matematicamente comprovado."),
                           ("pt", "Está provado sem sombra de dúvida.")):
            self.assertIn("SERIOUS", self.sev(text, lang), f"{lang}: {text}")

    def test_scoped_impossibility_is_exempt_in_each_language(self):
        self.assertEqual(self.sev("Esto es imposible sin una coalición.", "es"), [])
        self.assertEqual(self.sev("Das ist unmöglich ohne eine Koalition.", "de"), [])
        self.assertEqual(self.sev("Isso é impossível sem uma coalizão.", "pt"), [])
        self.assertIn("SERIOUS", self.sev("Das ist unmöglich.", "de"))

    def test_patterns_apply_to_their_own_language_only(self):
        # Spanish/Portuguese "definitivamente" is not scanned as English, and vice versa
        self.assertEqual(self.sev("Lo dijo definitivamente.", "en"), [])
        self.assertIn("SERIOUS", self.sev("Lo dijo definitivamente.", "es"))
        self.assertEqual(self.sev("Lo dijo obviamente.", "es"), ["MEDIUM"])


if __name__ == "__main__":
    unittest.main()

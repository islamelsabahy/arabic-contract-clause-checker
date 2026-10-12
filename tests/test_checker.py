# -*- coding: utf-8 -*-
import json
import os
import subprocess
import sys
import unittest

from contractcheck import analyze, normalize
from contractcheck.checker import render_text, to_dict

ROOT = os.path.join(os.path.dirname(__file__), "..")


def sample(name):
    with open(os.path.join(ROOT, "sample-data", name), encoding="utf-8") as fh:
        return fh.read()


def ids(report, kind=None, severity=None):
    return {f.id for f in report.findings
            if (kind is None or f.kind == kind) and (severity is None or f.severity == severity)}


class NormalizeTests(unittest.TestCase):
    def test_alef_ya_ta_marbuta(self):
        self.assertEqual(normalize("أإآ مدرسة على"), "ااا مدرسه علي")

    def test_diacritics_and_tatweel_removed(self):
        self.assertEqual(normalize("العَقْدُ"), "العقد")
        self.assertEqual(normalize("عـــقد"), "عقد")

    def test_arabic_digits(self):
        self.assertEqual(normalize("١٢٣ ۴۵۶ ٪"), "123 456 %")

    def test_whitespace_collapsed(self):
        self.assertEqual(normalize("  a \t  b "), "a b")


class SaleTests(unittest.TestCase):
    def test_good_contract_has_no_findings(self):
        r = analyze(sample("sale_good.txt"), "sale")
        self.assertEqual(r.findings, [], [(f.kind, f.id) for f in r.findings])
        self.assertEqual(len(r.clauses_found), r.clauses_checked)

    def test_risky_contract_flags_expected_risks(self):
        r = analyze(sample("sale_risky.txt"), "sale")
        self.assertEqual(
            ids(r, "risk"),
            {"non_refundable", "termination_no_notice", "automatic_termination", "open_delivery_extension",
             "sole_discretion", "uncapped_penalty", "waiver_of_rights", "blank_fields"},
        )

    def test_risky_contract_missing_clauses(self):
        r = analyze(sample("sale_risky.txt"), "sale")
        self.assertTrue({"parties", "property", "governing_law", "signatures", "date"} <= ids(r, "missing"))

    def test_findings_sorted_by_severity(self):
        r = analyze(sample("sale_risky.txt"), "sale")
        order = {"high": 3, "medium": 2, "low": 1}
        scores = [order[f.severity] for f in r.findings]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_diacritics_do_not_hide_a_risk(self):
        text = "وَكَافَّةُ الْمَبَالِغِ الْمُسَدَّدَةِ لَا تُرَدُّ لِلطَّرَفِ الثَّانِي."
        self.assertIn("non_refundable", ids(analyze(text), "risk"))

    def test_penalty_with_percentage_is_fine(self):
        text = "غرامة تأخير 1% شهرياً بحد أقصى 10%."
        self.assertNotIn("uncapped_penalty", ids(analyze(text), "risk"))

    def test_penalty_figure_in_next_sentence_of_same_paragraph_is_fine(self):
        text = "غرامة التأخير مستحقة. تحسب بواقع 2% شهرياً."
        self.assertNotIn("uncapped_penalty", ids(analyze(text), "risk"))

    def test_arabic_indic_digits_count_as_figures(self):
        self.assertNotIn("uncapped_penalty", ids(analyze("غرامة تأخير ٢ في الشهر"), "risk"))

    def test_prefixed_words_match(self):
        r = analyze("يخضع هذا العقد للقانون المصري وتختص محاكم القاهرة", "sale")
        self.assertNotIn("governing_law", ids(r, "missing"))

    def test_empty_text_reports_everything_missing(self):
        r = analyze("", "sale")
        self.assertEqual(len(ids(r, "missing")), r.clauses_checked)


class LeaseTests(unittest.TestCase):
    def test_lease_checks_lease_clauses_only(self):
        r = analyze(sample("lease_risky.txt"), "lease")
        self.assertIn("rent_increase", ids(r, "missing"))
        self.assertNotIn("price", ids(r, "missing"))
        self.assertNotIn("delivery_date", ids(r, "missing"))

    def test_lease_risks(self):
        r = analyze(sample("lease_risky.txt"), "lease")
        self.assertEqual(ids(r, "risk"), {"non_refundable", "uncapped_rent_increase"})

    def test_found_lease_clauses(self):
        r = analyze(sample("lease_risky.txt"), "lease")
        for cid in ("rent", "term", "purpose", "deposit", "governing_law", "date", "signatures", "parties", "property"):
            self.assertIn(cid, r.clauses_found)

    def test_invalid_kind(self):
        with self.assertRaises(ValueError):
            analyze("x", "mortgage")


class OutputTests(unittest.TestCase):
    def test_json_roundtrip(self):
        data = to_dict(analyze(sample("sale_risky.txt")))
        self.assertEqual(json.loads(json.dumps(data, ensure_ascii=False))["contract_kind"], "sale")
        self.assertIn("Not legal advice", data["disclaimer"])

    def test_text_in_both_languages(self):
        r = analyze(sample("sale_risky.txt"))
        self.assertIn("MISSING", render_text(r, "en"))
        self.assertIn("ناقص", render_text(r, "ar"))
        self.assertIn("Not legal advice", render_text(r, "en"))

    def test_cli_exit_codes(self):
        env = dict(os.environ, PYTHONPATH=ROOT, PYTHONIOENCODING="utf-8")
        def run(*args):
            return subprocess.run([sys.executable, "-m", "contractcheck", *args], cwd=ROOT, env=env,
                                  capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run("sample-data/sale_good.txt").returncode, 0)
        self.assertEqual(run("sample-data/sale_risky.txt").returncode, 1)
        self.assertEqual(run("sample-data/sale_risky.txt", "--fail-on", "none").returncode, 0)
        self.assertEqual(run("no-such-file.txt").returncode, 2)
        out = run("sample-data/sale_risky.txt", "--json").stdout
        self.assertEqual(json.loads(out)["contract_kind"], "sale")


if __name__ == "__main__":
    unittest.main()

import unittest

from helpers import EVID, Q, QIDS, TOTAL, WEIGHT, card, checks, run, vendor
from vqe import rating, validate


class TestQuestionSet(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(len(QIDS), 32)
        self.assertEqual(len(set(QIDS)), 32)
        self.assertEqual(len(Q["domains"]), 8)
        for d in Q["domains"]:
            self.assertEqual(sum(q["domain"] == d for q in Q["questions"]), 4, d)
        self.assertTrue(all(q["weight"] in (1, 2, 3) for q in Q["questions"]))

    def test_consistency_rules_reference_real_questions(self):
        for r in Q["consistency"]:
            self.assertIn(r["claim"], QIDS)
            self.assertIn(r["contradicted_by"], QIDS)


class TestScore(unittest.TestCase):
    def test_all_yes_with_evidence_is_100(self):
        c = card()
        self.assertEqual((c["claimed_score"], c["verified_score"], c["rating"]), (100.0, 100.0, "low"))

    def test_weighted_not_simple_average(self):
        c = card(answers={"ACC-3": "no"})                       # weight 3
        self.assertEqual(c["claimed_score"], round(100 * (TOTAL - 3) / TOTAL, 1))

    def test_partial_is_half(self):
        c = card(answers={"ACC-1": "partial"})                  # weight 3 loses 1.5
        self.assertEqual(c["claimed_score"], round(100 * (TOTAL - 1.5) / TOTAL, 1))

    def test_na_is_excluded_not_penalised(self):
        self.assertEqual(card(answers={"GOV-4": "na"})["claimed_score"], 100.0)

    def test_unsupported_yes_gets_half_credit_in_verified_only(self):
        c = card(evidence=[e for e in EVID if e != "iso27001_cert"])    # GOV-2 weight 3
        self.assertEqual(c["claimed_score"], 100.0)
        self.assertEqual(c["verified_score"], round(100 * (TOTAL - 1.5) / TOTAL, 1))

    def test_evidence_only_matters_for_yes(self):
        c = card(answers={"GOV-2": "no"}, evidence=[e for e in EVID if e != "iso27001_cert"])
        self.assertNotIn("UNSUPPORTED_YES", {i["check"] for i in run(answers={"GOV-2": "no"}, evidence=[e for e in EVID if e != "iso27001_cert"])["issues"]})
        self.assertEqual(c["claimed_score"], c["verified_score"])

    def test_domain_scores_and_weakest(self):
        c = card(answers={"ACC-1": "no", "ACC-2": "no", "ACC-3": "no", "ACC-4": "no", "DAT-1": "no"})
        self.assertEqual(c["domains"]["ACC"], 0.0)
        self.assertEqual(c["domains"]["GOV"], 100.0)
        self.assertEqual(c["weakest_domains"][:2], ["ACC", "DAT"])


class TestCoverage(unittest.TestCase):
    def answered(self, ids):
        return {q: ("yes" if q in ids else "unused") for q in QIDS}

    def test_boundary_at_80_percent_of_weight(self):
        # Answer questions in order until the answered weight first reaches 80%; dropping the last one must fall below it.
        keep, w = [], 0
        for q in sorted(QIDS):
            keep.append(q)
            w += WEIGHT[q]
            if w / TOTAL * 100 >= 80:
                break
        a = {q: "yes" for q in keep}
        v = validate([dict(vendor(), answers=a)], Q)
        from vqe import analyse
        c = analyse(v, Q)["scorecards"][0]
        self.assertGreaterEqual(c["answered_weight_pct"], 80)
        self.assertIsNotNone(c["claimed_score"])
        a.pop(keep[-1])
        c = analyse(validate([dict(vendor(), answers=a)], Q), Q)["scorecards"][0]
        self.assertLess(c["answered_weight_pct"], 80)
        self.assertIsNone(c["claimed_score"])
        self.assertEqual(c["rating"], "unrated")

    def test_exactly_80_percent_is_enough(self):
        # With five equally weighted questions, four answered is exactly 80%: inclusive boundary.
        small = dict(Q, questions=[{"id": f"X-{i}", "domain": "X", "weight": 1, "critical": False} for i in range(5)],
                     domains={"X": "X"}, consistency=[])
        from vqe import analyse
        four = {f"X-{i}": "yes" for i in range(4)}
        c = analyse(validate([dict(vendor(), answers=four)], small), small)["scorecards"][0]
        self.assertEqual((c["answered_weight_pct"], c["claimed_score"]), (80.0, 100.0))
        three = {f"X-{i}": "yes" for i in range(3)}
        c = analyse(validate([dict(vendor(), answers=three)], small), small)["scorecards"][0]
        self.assertIsNone(c["claimed_score"])

    def test_incomplete_flagged(self):
        v = dict(vendor(), answers={"GOV-1": "yes"})
        from vqe import analyse
        self.assertIn("INCOMPLETE", {i["check"] for i in analyse(validate([v], Q), Q)["issues"]})


class TestRating(unittest.TestCase):
    B = Q["bands"]

    def test_band_boundaries(self):
        for s, want in [(100, "low"), (80, "low"), (79.9, "medium"), (60, "medium"), (59.9, "high")]:
            self.assertEqual(rating(s, [], self.B), want, s)
        self.assertEqual(rating(None, [], self.B), "unrated")

    def test_critical_control_missing_floors_the_rating_at_medium(self):
        self.assertEqual(rating(95, ["ACC-3"], self.B), "medium")
        self.assertEqual(rating(70, ["ACC-3"], self.B), "medium")
        self.assertEqual(rating(40, ["ACC-3"], self.B), "high")
        self.assertEqual(card(answers={"ACC-3": "no"})["rating"], "medium")


class TestIssues(unittest.TestCase):
    def test_clean_vendor_has_none(self):
        self.assertEqual(run()["issues"], [])

    def test_unsupported_yes_severity_follows_weight(self):
        sev = {i["detail"][:5]: i["severity"] for i in run(evidence=[])["issues"] if i["check"] == "UNSUPPORTED_YES"}
        self.assertEqual(sev["GOV-1"], "high")      # weight 3
        self.assertEqual(sev["GOV-3"], "medium")    # weight 2

    def test_each_consistency_rule_fires_and_only_on_yes_vs_no(self):
        for r in Q["consistency"]:
            self.assertIn("INCONSISTENT_ANSWERS", checks(answers={r["contradicted_by"]: "no"}), r)
            others = {x["claim"]: "no" for x in Q["consistency"] if x["contradicted_by"] == r["contradicted_by"]}
            self.assertNotIn("INCONSISTENT_ANSWERS", checks(answers=dict(others, **{r["contradicted_by"]: "no"})), r)
            self.assertNotIn("INCONSISTENT_ANSWERS", checks(answers={r["contradicted_by"]: "partial"}), r)

    def test_critical_control_missing(self):
        crit = [q["id"] for q in Q["questions"] if q["critical"]]
        self.assertEqual(set(crit), {"ACC-3", "DAT-1", "INC-1"})
        for qid in crit:
            self.assertIn("CRITICAL_CONTROL_MISSING", checks(answers={qid: "no"}), qid)
            self.assertNotIn("CRITICAL_CONTROL_MISSING", checks(answers={qid: "partial"}), qid)

    def test_every_issue_has_a_question_to_send(self):
        res = run(answers={"ACC-3": "no", "SUB-1": "no"}, evidence=[])
        self.assertTrue(res["issues"] and all(i["question"].strip() for i in res["issues"]))


class TestValidation(unittest.TestCase):
    def test_bad_input(self):
        for kw in (dict(answers={"ZZZ-9": "yes"}), dict(answers={"GOV-1": "maybe"}), dict(tier=0)):
            with self.assertRaises(ValueError, msg=str(kw)):
                validate([vendor(**kw)], Q)
        with self.assertRaises(ValueError):
            validate([vendor(), vendor()], Q)

    def test_answers_are_case_insensitive(self):
        self.assertEqual(validate([vendor(answers={"GOV-1": "YES"})], Q)[0]["answers"]["GOV-1"], "yes")


if __name__ == "__main__":
    unittest.main()

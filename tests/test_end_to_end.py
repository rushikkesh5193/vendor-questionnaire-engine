import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from vqe import analyse, load, load_questions
from vqe.report import issues_csv, scorecards_csv, to_markdown

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "examples" / "sample_responses.json"
EXPECTED = {
    ("V001", "CRITICAL_CONTROL_MISSING"), ("V001", "INCONSISTENT_ANSWERS"), ("V002", "UNSUPPORTED_YES"),
    ("V003", "INCOMPLETE"), ("V004", "CRITICAL_CONTROL_MISSING"), ("V004", "RATING_HIGH"),
    ("V005", "INCONSISTENT_ANSWERS"), ("V006", "UNSUPPORTED_YES"), ("V007", "INCONSISTENT_ANSWERS"),
    ("V008", "CRITICAL_CONTROL_MISSING"), ("V008", "INCONSISTENT_ANSWERS"),
}


class TestSample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q = load_questions()
        cls.res = analyse(load(SAMPLE, cls.q), cls.q)

    def test_finds_exactly_the_injected_problems(self):
        got = {(i["vendor"], i["check"]) for i in self.res["issues"]}
        self.assertEqual(got - EXPECTED, set(), "false positives")
        self.assertEqual(EXPECTED - got, set(), "missed")

    def test_issue_counts_for_multi_hit_vendors(self):
        n = lambda v, c: sum(i["vendor"] == v and i["check"] == c for i in self.res["issues"])
        self.assertEqual(n("V005", "INCONSISTENT_ANSWERS"), 2)      # SUB-2 and SUB-3 both contradicted by SUB-1
        self.assertEqual(n("V004", "CRITICAL_CONTROL_MISSING"), 3)

    def test_clean_vendors_are_quiet_and_rated_low(self):
        for c in self.res["scorecards"]:
            if c["vendor"] > "V010":
                self.assertEqual((c["verified_score"], c["rating"]), (100.0, "low"), c["vendor"])
        self.assertEqual({i["vendor"] for i in self.res["issues"] if i["vendor"] > "V010"}, set())

    def test_scorecards(self):
        s = {c["vendor"]: c for c in self.res["scorecards"]}
        self.assertEqual(s["V001"]["rating"], "medium")        # 95.6 but a critical control is missing
        self.assertAlmostEqual(s["V002"]["claimed_score"] - s["V002"]["verified_score"], 2.2, places=6)
        self.assertEqual(s["V003"]["rating"], "unrated")
        self.assertEqual(s["V004"]["rating"], "high")

    def test_outputs(self):
        self.assertEqual(len(list(csv.reader(io.StringIO(issues_csv(self.res))))), len(self.res["issues"]) + 1)
        self.assertEqual(len(list(csv.reader(io.StringIO(scorecards_csv(self.res))))), 29)
        self.assertIn("not the SIG or CAIQ", to_markdown(self.res))


class TestCli(unittest.TestCase):
    def run_cli(self, *a):
        return subprocess.run([sys.executable, "-m", "vqe", *a], cwd=ROOT, capture_output=True, text=True)

    def test_writes_files(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_cli(str(SAMPLE), "--out-dir", d)
            self.assertEqual(r.returncode, 0, r.stderr)
            for f in ("report.md", "report.json", "scorecards.csv", "issues.csv"):
                self.assertTrue((Path(d) / f).is_file(), f)
            self.assertEqual(len(json.loads((Path(d) / "report.json").read_text())["issues"]), 14)

    def test_exit_codes(self):
        self.assertEqual(self.run_cli(str(SAMPLE), "--fail-on", "high").returncode, 1)
        self.assertEqual(self.run_cli("nope.json").returncode, 2)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "v.json"
            p.write_text(json.dumps([{"id": "A", "name": "a", "tier": 1, "answers": {"GOV-1": "maybe"}}]))
            r = self.run_cli(str(p))
            self.assertEqual(r.returncode, 2)
            self.assertIn("must be one of", r.stderr)


if __name__ == "__main__":
    unittest.main()

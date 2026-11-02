import argparse
import sys
from pathlib import Path

from . import analyse, load, load_questions
from .models import SEVERITIES
from .report import issues_csv, scorecards_csv, to_json, to_markdown


def main(argv=None):
    ap = argparse.ArgumentParser(prog="vqe", description="Score vendor security questionnaires and check them against evidence.")
    ap.add_argument("input")
    ap.add_argument("--questions", help="custom question set JSON")
    ap.add_argument("--out-dir")
    ap.add_argument("--fail-on", choices=SEVERITIES)
    a = ap.parse_args(argv)
    try:
        qset = load_questions(a.questions)
        res = analyse(load(a.input, qset), qset)
    except (OSError, ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if a.out_dir:
        d = Path(a.out_dir)
        d.mkdir(parents=True, exist_ok=True)
        (d / "report.md").write_text(to_markdown(res), encoding="utf-8")
        (d / "report.json").write_text(to_json(res), encoding="utf-8")
        (d / "scorecards.csv").write_text(scorecards_csv(res), encoding="utf-8")
        (d / "issues.csv").write_text(issues_csv(res), encoding="utf-8")
        print(f"{len(res['issues'])} issues -> {d}/")
    else:
        print(to_markdown(res))
    if a.fail_on and any(SEVERITIES.index(i["severity"]) <= SEVERITIES.index(a.fail_on) for i in res["issues"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

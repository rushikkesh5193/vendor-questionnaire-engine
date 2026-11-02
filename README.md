# vendor-questionnaire-engine

A small Python tool that scores vendor security questionnaires by control domain **and checks the answers against the evidence on file**. A vendor who answers "yes, we are ISO 27001 certified" with no certificate on file does not get full credit, and answers that contradict each other are flagged with a question to send back.

Python standard library only (tested on Python 3.13).

> **About the question set.** The 32 questions in `vqe/questions.json` are **my own, original**, written in the style of industry questionnaires (domains, weighted yes/partial/no answers, evidence). They are **not** the SIG (a proprietary Shared Assessments product) and **not** the CSA CAIQ. You can supply your own set with `--questions`.
>
> **Data note.** `examples/sample_responses.json` is **synthetic**. Eight of 28 vendors have problems injected on purpose and the tests check the tool finds exactly those. Nothing here comes from a real organisation.

## Quick start

```bash
python3 -m vqe examples/sample_responses.json --out-dir out    # report.md, report.json, scorecards.csv, issues.csv
python3 -m vqe examples/sample_responses.json --fail-on high   # exit 1 on any high issue
python3 -m unittest discover -s tests                          # 28 tests
bash scripts/run_demo.sh                                       # regenerate data, report and tests
```

## How it works

**Question set.** 8 domains (governance, access control, data protection, incident response, resilience, vulnerability management, secure development, fourth parties) with 4 questions each, weights 1 to 3. Some questions name the evidence that backs them up (for example the ISO 27001 certificate or the penetration test report). Three are *critical* controls (privileged MFA, encryption at rest, a documented incident response plan).

**Scores.** yes = 1, partial = 0.5, no = 0, n/a is left out. Two scores are produced:
- *Claimed*: answers at face value.
- *Verified*: a "yes" that needs evidence which is not on file only gets partial credit.

If under 80% of the question weight is answered, no score is given (`unrated`) rather than a guess.

**Rating** from the verified score: 80 and above is low risk, 60 to 79 medium, below 60 high. If a critical control is answered "no", the rating cannot be better than medium.

| Check | Raised when |
|---|---|
| `UNSUPPORTED_YES` | A yes where the required evidence is not on file (high for weight 3, else medium) |
| `INCONSISTENT_ANSWERS` | Two answers conflict, for example MFA claimed for all remote access but not for privileged accounts (7 rules in the question file) |
| `CRITICAL_CONTROL_MISSING` | A critical control answered no |
| `INCOMPLETE` | Too little of the questionnaire answered to score |
| `RATING_HIGH` | Verified score below the medium band |

Every issue carries the question to send back to the vendor.

## Limitations

- **Self-attested.** A vendor can answer "yes" and attach a document that does not say what they claim. The evidence check only tests that a document of the right type is on file, not what is in it (see `vendor-evidence-reviewer` for that).
- **The weights, bands and consistency rules are illustrative defaults**, not a standard. Tune them to your own risk appetite.
- **It cannot tell when an honest answer is wrong.** It finds contradictions, not mistakes that happen to be consistent.
- No persistence, UI or authentication. It reads JSON and writes reports.

## Layout

```
vqe/       models.py  analyse.py  report.py  questions.json  __main__.py
tools/     gen_sample.py     synthetic data generator
tests/     28 tests          incl. an exact-match end-to-end test
examples/  sample_responses.json  report.md  report.json  scorecards.csv  issues.csv
scripts/   run_demo.sh
```

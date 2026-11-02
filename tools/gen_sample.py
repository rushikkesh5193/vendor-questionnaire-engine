"""Synthetic questionnaire responses with problems injected on purpose.

    python3 -m tools.gen_sample examples/sample_responses.json
"""
import json
import sys

from vqe import load_questions

QS = load_questions()["questions"]
ALL_EVIDENCE = sorted({q["evidence"] for q in QS if "evidence" in q})


def clean(i, tier=2):
    return {"id": f"V{i:03d}", "name": f"Vendor {i:03d}", "tier": tier, "answers": {q["id"]: "yes" for q in QS},
            "evidence_on_file": list(ALL_EVIDENCE)}


def build():
    v = [clean(i, 1 + i % 4) for i in range(11, 31)]
    a = clean(1); a["answers"]["ACC-3"] = "no"                                           # contradicts ACC-1, and a critical control is missing
    b = clean(2); b["evidence_on_file"].remove("iso27001_cert")                           # claims ISO 27001, nothing on file
    c = clean(3); c["answers"] = {q["id"]: "yes" for q in QS[:14]}                        # only part answered
    d = clean(4); d["answers"] = {q["id"]: ("no" if q["id"][:3] in ("ACC", "DAT", "INC", "BCP", "VUL") else "partial") for q in QS}   # weak overall
    e = clean(5); e["answers"]["SUB-1"] = "no"                                            # contradicts SUB-2 and SUB-3
    f = clean(6); f["evidence_on_file"].remove("pentest_report")                          # claims annual pen test, no report
    g = clean(7); g["answers"]["BCP-1"] = "no"; g["evidence_on_file"].remove("bcp_plan")   # contradicts BCP-2 (DR tested, no plan)
    h = clean(8); h["answers"]["DAT-1"] = "no"                                            # critical control missing, and contradicts DAT-3
    return {"_note": "Synthetic data. Problems are injected on purpose.", "vendors": [a, b, c, d, e, f, g, h] + v}


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "examples/sample_responses.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(build(), fh, indent=2)
        fh.write("\n")

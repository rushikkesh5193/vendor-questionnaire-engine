import json
from pathlib import Path

SEVERITIES = ("critical", "high", "medium", "low")
ANSWERS = ("yes", "partial", "no", "na")


def load_questions(path=None):
    q = json.loads((Path(path) if path else Path(__file__).with_name("questions.json")).read_text(encoding="utf-8"))
    ids = [x["id"] for x in q["questions"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate question ids")
    for r in q["consistency"]:
        if r["claim"] not in ids or r["contradicted_by"] not in ids:
            raise ValueError(f"consistency rule uses unknown question: {r}")
    return q


def load(path, qset):
    with open(path, encoding="utf-8") as f:
        return validate(json.load(f), qset)


def validate(data, qset):
    rows = data["vendors"] if isinstance(data, dict) else data
    known = {q["id"] for q in qset["questions"]}
    out, seen = [], set()
    for v in rows:
        for k in ("id", "name", "tier"):
            if k not in v:
                raise ValueError(f"vendor {v.get('id', '?')}: missing {k}")
        if v["id"] in seen:
            raise ValueError(f"duplicate vendor id {v['id']}")
        seen.add(v["id"])
        if v["tier"] not in (1, 2, 3, 4):
            raise ValueError(f"vendor {v['id']}: tier must be 1..4")
        ans = {}
        for qid, a in v.get("answers", {}).items():
            if qid not in known:
                raise ValueError(f"vendor {v['id']}: unknown question {qid}")
            a = str(a).lower()
            if a not in ANSWERS:
                raise ValueError(f"vendor {v['id']}: answer to {qid} must be one of {ANSWERS}, got {a!r}")
            ans[qid] = a
        out.append(dict(v, answers=ans, evidence_on_file=set(v.get("evidence_on_file", []))))
    return out

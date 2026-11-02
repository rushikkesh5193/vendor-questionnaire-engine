from vqe import analyse, load_questions, validate

Q = load_questions()
QIDS = [q["id"] for q in Q["questions"]]
WEIGHT = {q["id"]: q["weight"] for q in Q["questions"]}
EVID = sorted({q["evidence"] for q in Q["questions"] if "evidence" in q})
TOTAL = sum(WEIGHT.values())


def vendor(answers=None, evidence=None, tier=2, **kw):
    a = {q: "yes" for q in QIDS}
    a.update(answers or {})
    d = {"id": "T1", "name": "Test", "tier": tier, "answers": a, "evidence_on_file": EVID if evidence is None else evidence}
    d.update(kw)
    return d


def run(**kw):
    return analyse(validate([vendor(**kw)], Q), Q)


def card(**kw):
    return run(**kw)["scorecards"][0]


def checks(**kw):
    return {i["check"] for i in run(**kw)["issues"]}

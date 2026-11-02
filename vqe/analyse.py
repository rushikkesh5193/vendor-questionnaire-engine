from .models import SEVERITIES

SEV = {s: i for i, s in enumerate(SEVERITIES)}


def _i(sev, v, check, detail, question):
    return {"severity": sev, "vendor": v["id"], "name": v["name"], "check": check, "detail": detail, "question": question}


def score(v, qset):
    """Return (claimed, verified, answered_weight_pct, domain_scores).
    claimed takes every answer at face value; verified gives an unsupported 'yes' only partial credit."""
    credit, unsup = qset["answer_credit"], qset["unsupported_yes_credit"]
    total = sum(q["weight"] for q in qset["questions"])
    dom = {}
    c_num = v_num = den = 0.0
    for q in qset["questions"]:
        a = v["answers"].get(q["id"])
        if a is None or a == "na":
            continue
        w = q["weight"]
        base = credit[a]
        ver = unsup if (a == "yes" and q.get("evidence") and q["evidence"] not in v["evidence_on_file"]) else base
        c_num += w * base
        v_num += w * ver
        den += w
        d = dom.setdefault(q["domain"], [0.0, 0.0, 0.0])
        d[0] += w * ver
        d[1] += w
    pct = 100 * den / total
    if pct < qset["min_answered_weight_pct"] or den == 0:
        return None, None, round(pct, 1), {k: round(100 * a / b, 1) for k, (a, b, _) in dom.items()}
    return round(100 * c_num / den, 1), round(100 * v_num / den, 1), round(pct, 1), {k: round(100 * a / b, 1) for k, (a, b, _) in dom.items()}


def rating(verified, critical_no, bands):
    if verified is None:
        return "unrated"
    r = "low" if verified >= bands["low_risk_min"] else ("medium" if verified >= bands["medium_risk_min"] else "high")
    if critical_no and r == "low":
        r = "medium"
    return r


def analyse(vendors, qset, as_of=None):
    Q = {q["id"]: q for q in qset["questions"]}
    issues, cards = [], []
    for v in vendors:
        claimed, verified, pct, dom = score(v, qset)
        found = []
        if claimed is None:
            found.append(_i("medium", v, "INCOMPLETE", f"Only {pct}% of the questionnaire weight is answered (minimum {qset['min_answered_weight_pct']}%).", "Please complete the unanswered questions."))
        for qid, a in v["answers"].items():
            q = Q[qid]
            if a == "yes" and q.get("evidence") and q["evidence"] not in v["evidence_on_file"]:
                found.append(_i("high" if q["weight"] >= 3 else "medium", v, "UNSUPPORTED_YES",
                                f"{qid} answered yes but no {q['evidence']} is on file.", f"You answered yes to {qid} ({q['text']}) Please provide the supporting evidence ({q['evidence']})."))
        for r in qset["consistency"]:
            if v["answers"].get(r["claim"]) == "yes" and v["answers"].get(r["contradicted_by"]) == "no":
                found.append(_i("high", v, "INCONSISTENT_ANSWERS", f"{r['claim']} yes but {r['contradicted_by']} no: {r['why']}.", f"Your answers to {r['claim']} and {r['contradicted_by']} conflict. Please clarify."))
        critical_no = [qid for qid, a in v["answers"].items() if a == "no" and Q[qid]["critical"]]
        for qid in critical_no:
            found.append(_i("high", v, "CRITICAL_CONTROL_MISSING", f"{qid} answered no: {Q[qid]['text']}", f"What is your plan and date to implement {qid}?"))
        rate = rating(verified, critical_no, qset["bands"])
        if rate == "high":
            found.append(_i("high", v, "RATING_HIGH", f"Verified score {verified} is below {qset['bands']['medium_risk_min']}.", "Request a remediation plan before proceeding."))
        weakest = sorted(dom.items(), key=lambda kv: (kv[1], kv[0]))[:3]
        cards.append({"vendor": v["id"], "name": v["name"], "tier": v["tier"], "claimed_score": claimed, "verified_score": verified,
                      "answered_weight_pct": pct, "rating": rate, "domains": dom, "weakest_domains": [d for d, _ in weakest]})
        issues += found
    issues.sort(key=lambda i: (SEV[i["severity"]], i["vendor"], i["check"], i["detail"]))
    return {"as_of": str(as_of) if as_of else "", "issues": issues, "scorecards": cards, "domains": qset["domains"]}

import csv
import io
import json


def scorecards_csv(res):
    b = io.StringIO()
    w = csv.writer(b, lineterminator="\n")
    w.writerow(["vendor", "name", "tier", "claimed_score", "verified_score", "answered_weight_pct", "rating", "weakest_domains"])
    for c in res["scorecards"]:
        w.writerow([c["vendor"], c["name"], c["tier"], "" if c["claimed_score"] is None else c["claimed_score"],
                    "" if c["verified_score"] is None else c["verified_score"], c["answered_weight_pct"], c["rating"], " ".join(c["weakest_domains"])])
    return b.getvalue()


def issues_csv(res):
    b = io.StringIO()
    w = csv.writer(b, lineterminator="\n")
    w.writerow(["severity", "vendor", "name", "check", "detail", "question"])
    w.writerows([[i["severity"], i["vendor"], i["name"], i["check"], i["detail"], i["question"]] for i in res["issues"]])
    return b.getvalue()


def to_json(res):
    return json.dumps(res, indent=2)


def to_markdown(res):
    L = ["# Vendor questionnaire scoring", "",
         "Scores come from an original SIG/CAIQ-style question set (not the SIG or CAIQ). *Claimed* takes answers at face value; "
         "*verified* gives an unsupported yes only partial credit.", "",
         "| Vendor | Tier | Claimed | Verified | Rating | Weakest domains |", "|---|---|---|---|---|---|"]
    for c in sorted(res["scorecards"], key=lambda c: (c["verified_score"] is None, c["verified_score"] or 0)):
        L.append(f"| {c['name']} (`{c['vendor']}`) | {c['tier']} | {c['claimed_score'] if c['claimed_score'] is not None else '-'} | "
                 f"{c['verified_score'] if c['verified_score'] is not None else '-'} | {c['rating']} | {', '.join(res['domains'][d] for d in c['weakest_domains'])} |")
    L += ["", "## Issues", ""]
    for sev in ("critical", "high", "medium", "low"):
        rows = [i for i in res["issues"] if i["severity"] == sev]
        if rows:
            L += [f"### {sev.title()} ({len(rows)})", ""] + [f"- **{i['check']}** {i['name']} (`{i['vendor']}`): {i['detail']}" for i in rows] + [""]
    return "\n".join(L) + "\n"

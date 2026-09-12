"""Run the three policies over the labeled cases and score them.

Labels are hidden at decision time (the deciders never see `true_world`); we
reveal it only to score -- "no marking our own paper" (section 2).

Metrics (section 9 + the r/learnmachinelearning discussion):
  - decision cost (the primary axis, Chapter 0 cost lens)
  - human-review rate (fraction sent to FLAG)
  - confusion matrix (action x true_world) + per-action correctness
  - precision / recall for the ACCEPT-is-safe decision
  - calibration: reliability by P(correct) confidence bin
  - agreement % between the full belief policy and the dumb baseline
    (PLBjt's "if they agree ~95%, the Bayesian bit isn't paying rent" test)

Writes JSON + human-readable text to results/.
"""

from __future__ import annotations

import json
import math
import os
from typing import Dict, List, Tuple

from agent import POLICIES
from domain import COST, WORLDS

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cases.jsonl")
RESULTS = os.path.join(HERE, "..", "results")

# Which (action, true_world) pairs count as a "good call" for accuracy.
# ACCEPT good only if correct; REPAIR good for repairable flaws; REJECT/FLAG are
# safe (never publish a lie) so counted non-harmful; BUY is a non-terminal step.
GOOD = {
    "ACCEPT": {"correct"},
    "REPAIR": {"unit_error", "typo", "wrong_product"},
    "REJECT": {"missing", "garbled", "typo", "wrong_product", "unit_error", "correct"},
    "FLAG": set(WORLDS),   # flagging is always "safe" (a human decides)
    "BUY": set(WORLDS),
}


def load_cases() -> List[dict]:
    with open(DATA) as f:
        return [json.loads(line) for line in f if line.strip()]


def run_policy(name: str, cases: List[dict]) -> List[dict]:
    decide = POLICIES[name]
    out = []
    for c in cases:
        d = decide(c["source"], c["initial_signals"], c.get("extra_signals"))
        d["case_id"] = c["case_id"]
        d["true_world"] = c["true_world"]  # revealed only now, for scoring
        d["cost"] = COST[d["action"]][c["true_world"]]
        out.append(d)
    return out


def confusion(decisions: List[dict]) -> Dict[str, Dict[str, int]]:
    m: Dict[str, Dict[str, int]] = {}
    for d in decisions:
        m.setdefault(d["action"], {w: 0 for w in WORLDS})
        m[d["action"]][d["true_world"]] += 1
    return m


def accept_precision_recall(decisions: List[dict]) -> Dict[str, float]:
    """Treat ACCEPT as the positive 'this value is safe to publish' decision.
    precision = of things we ACCEPTed, how many were truly correct.
    recall    = of truly-correct values, how many did we ACCEPT."""
    tp = sum(1 for d in decisions if d["action"] == "ACCEPT" and d["true_world"] == "correct")
    fp = sum(1 for d in decisions if d["action"] == "ACCEPT" and d["true_world"] != "correct")
    fn = sum(1 for d in decisions if d["action"] != "ACCEPT" and d["true_world"] == "correct")
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return {"accept_precision": round(precision, 3),
            "accept_recall": round(recall, 3),
            "true_accepts": tp, "false_accepts": fp, "missed_accepts": fn}


def calibration_bins(decisions: List[dict]) -> List[dict]:
    """Reliability by confidence bin (Q3). For each P(correct) bucket, report the
    empirical fraction of cases that truly were `correct`."""
    edges = [(0.0, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 0.95), (0.95, 1.01)]
    bins = []
    for lo, hi in edges:
        members = [d for d in decisions if lo <= d["p_correct"] < hi]
        if not members:
            bins.append({"bin": f"{lo:.2f}-{hi:.2f}", "n": 0,
                         "mean_pred": None, "empirical_correct": None})
            continue
        mean_pred = sum(d["p_correct"] for d in members) / len(members)
        emp = sum(1 for d in members if d["true_world"] == "correct") / len(members)
        bins.append({"bin": f"{lo:.2f}-{hi:.2f}", "n": len(members),
                     "mean_pred": round(mean_pred, 3),
                     "empirical_correct": round(emp, 3)})
    return bins


def summarize(name: str, decisions: List[dict]) -> dict:
    n = len(decisions)
    total_cost = sum(d["cost"] for d in decisions)
    human = sum(1 for d in decisions if d["action"] == "FLAG")
    buys = sum(d["buys"] for d in decisions)
    wrong_publishes = sum(1 for d in decisions if d["action"] == "ACCEPT"
                          and d["true_world"] != "correct")
    return {
        "policy": name,
        "n_cases": n,
        "total_cost": total_cost,
        "avg_cost": round(total_cost / n, 3),
        "human_review_rate": round(human / n, 3),
        "total_buys": buys,
        "wrong_publishes_cost20": wrong_publishes,
        "accept_metrics": accept_precision_recall(decisions),
        "confusion": confusion(decisions),
        "calibration": calibration_bins(decisions),
    }


def agreement(a: List[dict], b: List[dict]) -> dict:
    """Fraction of cases where two policies pick the same action."""
    by_id_b = {d["case_id"]: d["action"] for d in b}
    same = sum(1 for d in a if by_id_b.get(d["case_id"]) == d["action"])
    return {"agree_fraction": round(same / len(a), 3), "same": same, "n": len(a)}


def _normal_cdf(z: float) -> float:
    """Standard-normal CDF via the error function (stdlib only)."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def paired_wilcoxon(a: List[dict], b: List[dict]) -> dict:
    """Paired Wilcoxon signed-rank test on per-case cost differences (a - b).

    Requested by the AI probability review (Sec 11): a 0.8-unit average-cost gap on
    N=40 with a skewed, spiky cost distribution (one cost-20 event moves the mean by
    ~0.5) needs a paired significance test before it counts as a *finding*, not a
    point estimate. We pair by case_id (same 40 cases, so the pairing is exact) and
    use the normal approximation to the signed-rank statistic with tie/zero handling.
    Pure stdlib; no scipy. Returns the two-sided p-value and the median difference.
    """
    by_id_b = {d["case_id"]: d for d in b}
    diffs = [d["cost"] - by_id_b[d["case_id"]]["cost"]
             for d in a if d["case_id"] in by_id_b]
    n_total = len(diffs)
    nonzero = [x for x in diffs if x != 0]
    n = len(nonzero)
    result = {
        "n_pairs": n_total,
        "n_nonzero": n,
        "median_diff": round(_median(diffs), 3) if diffs else None,
        "mean_diff": round(sum(diffs) / n_total, 3) if n_total else None,
    }
    if n < 1:
        result.update({"W": None, "z": None, "p_two_sided": None,
                       "note": "no non-zero differences; test undefined"})
        return result

    # rank the absolute non-zero differences, averaging tied ranks
    order = sorted(range(n), key=lambda i: abs(nonzero[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(nonzero[order[j + 1]]) == abs(nonzero[order[i]]):
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0  # ranks are 1-based
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1

    w_plus = sum(r for x, r in zip(nonzero, ranks) if x > 0)
    w_minus = sum(r for x, r in zip(nonzero, ranks) if x < 0)
    w = min(w_plus, w_minus)

    mean_w = n * (n + 1) / 4.0
    var_w = n * (n + 1) * (2 * n + 1) / 24.0
    if var_w == 0:
        result.update({"W": w, "z": None, "p_two_sided": None,
                       "note": "zero variance; test undefined"})
        return result
    # continuity-corrected z
    z = (w - mean_w + 0.5) / math.sqrt(var_w) if w < mean_w else \
        (w - mean_w - 0.5) / math.sqrt(var_w)
    p_two_sided = 2.0 * _normal_cdf(-abs(z))
    result.update({
        "W": round(w, 2),
        "w_plus": round(w_plus, 2),
        "w_minus": round(w_minus, 2),
        "z": round(z, 3),
        "p_two_sided": round(min(1.0, p_two_sided), 4),
        "significant_at_0.05": bool(p_two_sided < 0.05),
        "note": ("normal approximation with continuity correction; small N -- read "
                 "as indicative, not definitive"),
    })
    return result


def _median(xs: List[float]) -> float:
    s = sorted(xs)
    m = len(s)
    if m == 0:
        return 0.0
    if m % 2 == 1:
        return float(s[m // 2])
    return (s[m // 2 - 1] + s[m // 2]) / 2.0


def main() -> None:
    os.makedirs(RESULTS, exist_ok=True)
    cases = load_cases()

    runs = {name: run_policy(name, cases) for name in POLICIES}
    summaries = {name: summarize(name, runs[name]) for name in POLICIES}

    # PLBjt's rent test: full belief policy vs. dumb baseline.
    rent = agreement(runs["full"], runs["baseline"])

    # AI probability review (Sec 11): paired significance test on the cost gap.
    cost_test_baseline = paired_wilcoxon(runs["full"], runs["baseline"])
    cost_test_autonomous = paired_wilcoxon(runs["full"], runs["autonomous"])

    report = {
        "n_cases": len(cases),
        "summaries": summaries,
        "belief_vs_baseline_agreement": rent,
        "rent_verdict": (
            "belief layer NOT clearly paying rent (>=95% agreement with baseline)"
            if rent["agree_fraction"] >= 0.95 else
            "belief layer changes decisions vs. baseline (but see significance test)"
        ),
        "cost_significance": {
            "full_vs_baseline": cost_test_baseline,
            "full_vs_autonomous": cost_test_autonomous,
            "interpretation": (
                "Paired Wilcoxon signed-rank on per-case cost differences. If "
                "p >= 0.05 the average-cost gap is NOT statistically significant at "
                "N=40 -- the lower mean cost is a point estimate, not a proven win "
                "(and note it is largely bought by a higher FLAG/escalation rate)."
            ),
        },
    }

    with open(os.path.join(RESULTS, "metrics.json"), "w") as f:
        json.dump(report, f, indent=2)

    # per-decision audit rows (Step-10 format) for each policy
    for name, decs in runs.items():
        with open(os.path.join(RESULTS, f"decisions_{name}.jsonl"), "w") as f:
            for d in decs:
                f.write(json.dumps(d) + "\n")

    _write_text_report(report)
    print(f"scored {len(cases)} cases across {len(POLICIES)} policies -> results/")
    for name, s in summaries.items():
        print(f"  {name:11s} avg_cost={s['avg_cost']:6.3f} "
              f"human={s['human_review_rate']:.2f} "
              f"wrong_publishes={s['wrong_publishes_cost20']}")
    print(f"  belief-vs-baseline agreement = {rent['agree_fraction']:.2f} "
          f"-> {report['rent_verdict']}")
    ctb = cost_test_baseline
    print(f"  cost full-vs-baseline: median_diff={ctb['median_diff']} "
          f"p={ctb['p_two_sided']} "
          f"(significant@0.05={ctb.get('significant_at_0.05')})")


def _write_text_report(report: dict) -> None:
    lines = ["# Results -- belief engine vs. autonomous vs. baseline", ""]
    lines.append(f"Cases: {report['n_cases']}")
    lines.append("")
    lines.append("| policy | avg cost | human-review rate | wrong publishes (cost 20) | accept precision | accept recall |")
    lines.append("|--------|:---:|:---:|:---:|:---:|:---:|")
    for name, s in report["summaries"].items():
        am = s["accept_metrics"]
        lines.append(f"| {name} | {s['avg_cost']} | {s['human_review_rate']} | "
                     f"{s['wrong_publishes_cost20']} | {am['accept_precision']} | "
                     f"{am['accept_recall']} |")
    lines.append("")
    lines.append(f"**Belief-vs-baseline agreement:** {report['belief_vs_baseline_agreement']['agree_fraction']} "
                 f"-> {report['rent_verdict']}")
    lines.append("")
    sig = report["cost_significance"]
    lines.append("## Is the cost gap statistically significant? (paired Wilcoxon signed-rank)")
    lines.append("")
    lines.append("| comparison | median cost diff | mean cost diff | W | z | p (two-sided) | significant @0.05 |")
    lines.append("|---|:---:|:---:|:---:|:---:|:---:|:---:|")
    for label, key in [("full vs baseline", "full_vs_baseline"),
                       ("full vs autonomous", "full_vs_autonomous")]:
        t = sig[key]
        lines.append(f"| {label} | {t.get('median_diff')} | {t.get('mean_diff')} | "
                     f"{t.get('W')} | {t.get('z')} | {t.get('p_two_sided')} | "
                     f"{t.get('significant_at_0.05')} |")
    lines.append("")
    lines.append(f"_{sig['interpretation']}_")
    lines.append("")
    for name, s in report["summaries"].items():
        lines.append(f"## Calibration -- {name}")
        lines.append("| P(correct) bin | n | mean predicted | empirical correct |")
        lines.append("|---|:---:|:---:|:---:|")
        for b in s["calibration"]:
            lines.append(f"| {b['bin']} | {b['n']} | {b['mean_pred']} | {b['empirical_correct']} |")
        lines.append("")
    with open(os.path.join(RESULTS, "report.md"), "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()

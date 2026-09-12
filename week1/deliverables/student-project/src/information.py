"""Week-2 information layer: entropy, expected bits-per-cost, and true VOI.

Every number in sections 9-13 of `decisions/belief-engine-decision-model.md`
(and the Week-2 half of `paper/preprint.tex` + `decisions/information-decision-record.md`)
is reproduced here from committed code, so the markdown can never silently drift
from an un-tracked scratch script. As with `domain.py`, if code and the markdown
model disagree, the markdown is the design and this file has the bug.

Stdlib only (`math`). Reuses the exact belief mechanics and cost matrix from the
Week-1 modules, so the two layers share one source of truth.

Run:  python src/information.py         # prints the section-by-section trace
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from domain import COST, WORLDS
from agent import bayes_update, expected_loss

Belief = Dict[str, float]

# --- the locked worked case (section 4.3 post-oos posterior) ----------------
# Chained MID prior -> out-of-support update. We recompute it from domain.py so
# it stays tied to the Week-1 numbers rather than being pasted in.
from agent import prior_belief, update_all

POST_OOS: Belief = update_all(prior_belief("MID"), ["oos"])

# --- Week-2 clue likelihood models (decision model section 10.1) ------------
# Author-set, reasoned world-by-world. Each entry is P(clue returns the
# "16 GB"-consistent / positive outcome | world). Two-outcome tests.
CLUES: Dict[str, Dict[str, object]] = {
    "manufacturer": {
        "cost": 2,
        "P_pos": {  # section 10.1, revised row
            "correct": 0.90, "wrong_product": 0.15, "unit_error": 0.82,
            "typo": 0.35, "missing": 0.05, "garbled": 0.05,
        },
    },
    "cross_source": {  # curated near-independent panel (sharper row)
        "cost": 1,
        "P_pos": {
            "correct": 0.75, "wrong_product": 0.20, "unit_error": 0.65,
            "typo": 0.28, "missing": 0.10, "garbled": 0.10,
        },
    },
    "reference": {  # scraped/stale catalogue (near-flat row => weak)
        "cost": 1,
        "P_pos": {
            "correct": 0.65, "wrong_product": 0.40, "unit_error": 0.55,
            "typo": 0.35, "missing": 0.15, "garbled": 0.15,
        },
    },
}

TERMINALS = ["ACCEPT", "REPAIR", "FLAG", "REJECT"]


# --- entropy / information (section 9) --------------------------------------

def entropy(belief: Belief) -> float:
    """H(belief) = -sum p log2 p, in bits. 0 log 0 := 0."""
    return -sum(p * math.log2(p) for p in belief.values() if p > 0)


def _posterior_two_outcome(belief: Belief, p_pos: Dict[str, float]
                           ) -> Tuple[float, Belief, Belief]:
    """Split a belief through a two-outcome test.

    Returns (P(positive), belief|positive, belief|negative), each renormalised.
    """
    pos_num = {w: belief[w] * p_pos[w] for w in WORLDS}
    neg_num = {w: belief[w] * (1.0 - p_pos[w]) for w in WORLDS}
    p_positive = sum(pos_num.values())
    p_negative = sum(neg_num.values())
    post_pos = ({w: pos_num[w] / p_positive for w in WORLDS}
                if p_positive > 0 else dict(belief))
    post_neg = ({w: neg_num[w] / p_negative for w in WORLDS}
                if p_negative > 0 else dict(belief))
    return p_positive, post_pos, post_neg


def expected_info_gain(belief: Belief, p_pos: Dict[str, float]) -> dict:
    """Expected information gain (= mutual information) of a two-outcome clue.

    E[gain] = H(belief) - [ P(pos) H(belief|pos) + P(neg) H(belief|neg) ].
    Also returns the per-branch entropies so section 12's 'does evidence raise
    uncertainty?' check is auditable.
    """
    h0 = entropy(belief)
    p_positive, post_pos, post_neg = _posterior_two_outcome(belief, p_pos)
    h_pos, h_neg = entropy(post_pos), entropy(post_neg)
    cond_h = p_positive * h_pos + (1.0 - p_positive) * h_neg
    return {
        "H0": h0, "P_pos": p_positive,
        "H_pos": h_pos, "H_neg": h_neg,
        "cond_H": cond_h, "E_gain": h0 - cond_h,
        "post_pos": post_pos, "post_neg": post_neg,
    }


# --- value of information (section 11) --------------------------------------

def best_terminal(belief: Belief) -> Tuple[str, float]:
    a = min(TERMINALS, key=lambda x: expected_loss(belief, x))
    return a, expected_loss(belief, a)


def voi(belief: Belief, p_pos: Dict[str, float]) -> dict:
    """True value of information (section 11).

    VOI = E[loss | best terminal now] - E[loss | best terminal after the clue],
    with the post-clue term averaged over the clue's two outcomes (re-selecting
    the cheapest terminal action in each branch).
    """
    _, loss_now = best_terminal(belief)
    p_positive, post_pos, post_neg = _posterior_two_outcome(belief, p_pos)
    _, loss_pos = best_terminal(post_pos)
    _, loss_neg = best_terminal(post_neg)
    loss_after = p_positive * loss_pos + (1.0 - p_positive) * loss_neg
    return {"loss_now": loss_now, "loss_after": loss_after,
            "VOI": loss_now - loss_after}


# --- section 13.1: the falsified 'make the human expensive' experiment ------

def voi_vs_flag_cost(belief: Belief, flag_costs: List[float]) -> List[dict]:
    """Sweep the FLAG cost and recompute VOI for each clue.

    Tests the hypothesis 'raising the human cost revives buying'. We override
    only FLAG's (world-independent) cost and leave every other cost fixed.
    """
    saved = dict(COST["FLAG"])
    rows = []
    try:
        for fc in flag_costs:
            for w in WORLDS:
                COST["FLAG"][w] = fc
            act_now, loss_now = best_terminal(belief)
            row = {"flag_cost": fc, "fallback": act_now, "loss_now": loss_now}
            for name, spec in CLUES.items():
                row[name] = round(voi(belief, spec["P_pos"])["VOI"], 3)
            rows.append(row)
    finally:
        COST["FLAG"].update(saved)  # never leave the shared matrix mutated
    return rows


# --- reporting --------------------------------------------------------------

def _fmt_belief(b: Belief) -> str:
    return " ".join(f"{w[:4]}={b[w]:.3f}" for w in WORLDS)


def main() -> None:
    b = POST_OOS
    print("=== Section 9: entropy on the 160 GB case ===")
    prior = prior_belief("MID")
    print(f"prior  H = {entropy(prior):.3f} bits   [{_fmt_belief(prior)}]")
    print(f"post-oos H = {entropy(b):.3f} bits   [{_fmt_belief(b)}]")
    print(f"observed gain (oos=true) = {entropy(prior) - entropy(b):.3f} bits\n")

    print("=== Section 10: which clue to buy next (expected bits per cost) ===")
    ranking = []
    for name, spec in CLUES.items():
        r = expected_info_gain(b, spec["P_pos"])
        cost = spec["cost"]
        ranking.append((name, r["E_gain"], cost, r["E_gain"] / cost,
                        r["H_pos"], r["H_neg"]))
        print(f"{name:13s} cost={cost}  P(pos)={r['P_pos']:.3f}  "
              f"E[gain]={r['E_gain']:.3f} bits  bits/cost={r['E_gain']/cost:.3f}  "
              f"(H|pos={r['H_pos']:.3f} H|neg={r['H_neg']:.3f})")
    most_bits = max(ranking, key=lambda x: x[1])
    best_percost = max(ranking, key=lambda x: x[3])
    print(f"-> most informative : {most_bits[0]} ({most_bits[1]:.3f} bits)")
    print(f"-> best per rupee   : {best_percost[0]} ({best_percost[3]:.3f} bits/cost)")
    print(f"-> rankings {'DISAGREE' if most_bits[0]!=best_percost[0] else 'agree'}\n")

    print("=== Section 11: true value of information (should stop / buy?) ===")
    act, loss = best_terminal(b)
    print(f"best terminal now = {act} @ E[loss]={loss:.2f}")
    for name, spec in CLUES.items():
        v = voi(b, spec["P_pos"])
        net = v["VOI"] - spec["cost"]
        print(f"{name:13s} VOI={v['VOI']:.3f}  net(VOI-cost)={net:+.3f}  "
              f"-> {'BUY' if net > 0 else 'do not buy'}")
    print()

    print("=== Section 12b: does any clue branch RAISE entropy? ===")
    raised = False
    for name, spec in CLUES.items():
        r = expected_info_gain(b, spec["P_pos"])
        for branch, h in (("pos", r["H_pos"]), ("neg", r["H_neg"])):
            if h > entropy(b):
                raised = True
                print(f"  {name} [{branch}] H={h:.3f} > start {entropy(b):.3f}  RAISES")
    print(f"  -> {'some branch raises entropy' if raised else 'NO branch raises entropy (claim dropped, per model 12.2)'}\n")

    print("=== Section 13.1: 'make the human expensive' (FALSIFIED hypothesis) ===")
    print(f"{'FLAG':>5} {'fallback':>8} {'manufacturer':>13} {'cross_source':>13} {'reference':>10}")
    for row in voi_vs_flag_cost(b, [2, 4, 5, 10, 15]):
        print(f"{row['flag_cost']:>5} {row['fallback']:>8} "
              f"{row['manufacturer']:>13} {row['cross_source']:>13} {row['reference']:>10}")
    print("  -> VOI rises off zero but plateaus below clue cost: buying never revives.")


if __name__ == "__main__":
    main()

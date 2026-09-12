"""Generate the labeled evaluation set.

Two parts (Q2 option a):
  1. SEED rows -- the 14 hand-designed cases transcribed from section 7 of the
     decision model (including the two deliberate failure seeds).
  2. SAMPLED rows -- expand toward ~40 by drawing a hidden true world from a
     source prior (section 3) and then sampling evidence signals consistent with
     that world's likelihoods (section 4).

Each row = {case_id, field, source, true_world (HIDDEN at decision time),
initial_signals, extra_signals}. `extra_signals` are what a BUY would reveal.

Deterministic: fixed seed so results reproduce (ties to the Step-10
reproducibility statement).
"""

from __future__ import annotations

import json
import os
import random
from typing import Dict, List

from domain import LIKELIHOODS, PRIORS, WORLDS

SEED = 20260830
FIELDS = ["ram_gb", "storage_gb", "weight_g", "screen_in", "battery_mah"]

# The evidence signals a world can plausibly emit, for sampling (section 4).
# For each world we list the signals to consider; each is included in a row with
# probability = its likelihood for that world.
CANDIDATE_SIGNALS = ["oos", "unit", "xsource_agree", "xsource_disagree",
                     "empty", "junk"]


def seed_rows() -> List[dict]:
    """The 14 section-7 cases. `extra` = what a buy reveals (may be empty)."""
    R = lambda cid, field, src, world, init, extra: {
        "case_id": cid, "field": field, "source": src, "true_world": world,
        "initial_signals": init, "extra_signals": extra,
    }
    return [
        R("seed01", "ram_gb", "MFR", "correct", ["xsource_agree"], []),
        R("seed02", "ram_gb", "MID", "typo", ["oos"], ["xsource_disagree"]),
        R("seed03", "storage_gb", "MID", "unit_error", ["unit"], []),
        R("seed04", "ram_gb", "SKY", "correct", [], ["xsource_agree"]),
        R("seed05", "ram_gb", "MFR", "wrong_product", ["xsource_disagree"], ["xsource_disagree"]),
        R("seed06", "weight_g", "MID", "typo", ["oos"], []),
        R("seed07", "battery_mah", "MID", "missing", ["empty"], []),
        R("seed08", "ram_gb", "MID", "garbled", ["junk"], []),
        R("seed09", "storage_gb", "MFR", "correct", ["xsource_agree"], []),
        R("seed10", "ram_gb", "SKY", "correct", ["xsource_agree"], ["xsource_agree"]),
        # rows 11-12: deliberate FAILURE SEEDS (wrong_product that looks normal
        # and even has cross-source agreement -- section 8 F1/F2).
        R("seed11", "screen_in", "MFR", "wrong_product", ["xsource_agree"], ["xsource_agree"]),
        R("seed12", "ram_gb", "MFR", "wrong_product", ["xsource_agree"], ["xsource_agree"]),
        R("seed13", "storage_gb", "MID", "unit_error", ["unit"], []),
        R("seed14", "battery_mah", "SKY", "typo", ["oos"], ["xsource_disagree"]),
    ]


def _sample_world(rng: random.Random, source: str) -> str:
    tokens = PRIORS[source]
    total = sum(tokens.values())
    r = rng.uniform(0, total)
    acc = 0.0
    for w in WORLDS:
        acc += tokens[w]
        if r <= acc:
            return w
    return WORLDS[-1]


def _sample_signals(rng: random.Random, world: str) -> List[str]:
    """Draw evidence for a world: each candidate signal fires with prob =
    its likelihood for that world. Guarantees at least one signal so the row is
    decidable (falls back to the world's most likely signal)."""
    fired = []
    for sig in CANDIDATE_SIGNALS:
        p = LIKELIHOODS[sig][world]
        if rng.random() < p:
            fired.append(sig)
    # de-conflict impossible combos: empty/junk are terminal readings
    if "empty" in fired:
        fired = ["empty"]
    elif "junk" in fired:
        fired = ["junk"]
    if not fired:
        best = max(CANDIDATE_SIGNALS, key=lambda s: LIKELIHOODS[s][world])
        fired = [best]
    return fired


def sampled_rows(rng: random.Random, n: int) -> List[dict]:
    rows = []
    sources = ["MFR", "MID", "SKY"]
    for i in range(n):
        source = rng.choice(sources)
        world = _sample_world(rng, source)
        signals = _sample_signals(rng, world)
        # a possible second clue a BUY could reveal (also world-consistent)
        extra = _sample_signals(rng, world)
        rows.append({
            "case_id": f"gen{i+1:03d}",
            "field": rng.choice(FIELDS),
            "source": source,
            "true_world": world,
            "initial_signals": signals,
            "extra_signals": extra,
        })
    return rows


def build(n_sampled: int = 26) -> List[dict]:
    rng = random.Random(SEED)
    rows = seed_rows() + sampled_rows(rng, n_sampled)  # 14 + 26 = 40
    return rows


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "data", "cases.jsonl")
    rows = build()
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} labeled cases to {os.path.relpath(out)}")


if __name__ == "__main__":
    main()

"""The belief engine + decision policies.

Transcribes sections 4 (Bayes update) and 6 (expected-loss policy, thresholds,
VOI, buy-cap) of `decisions/belief-engine-decision-model.md`.

Three deciders are provided:
  - decide_full        : Policy A -- belief + expected loss + BUY + FLAG.
  - decide_autonomous  : Policy B -- belief + expected loss, NO human, NO buy
                         (ACCEPT / REPAIR / REJECT only).
  - decide_baseline    : the "dumb" calibrated-score + threshold policy the
                         r/learnmachinelearning discussion asked for.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from domain import (
    ACCEPT_THRESHOLD,
    COST,
    LIKELIHOODS,
    MAX_BUYS,
    PRIORS,
    TERMINAL_ACTIONS,
    WORLDS,
)

Belief = Dict[str, float]


# --- belief mechanics (section 4) ------------------------------------------

def prior_belief(source: str) -> Belief:
    """Normalized prior for a source tier (section 3.1)."""
    tokens = PRIORS[source]
    total = sum(tokens.values())
    return {w: tokens[w] / total for w in WORLDS}


def bayes_update(belief: Belief, signal: str) -> Belief:
    """prior x likelihood, then normalize (section 4.3 / 4.4)."""
    like = LIKELIHOODS[signal]
    surviving = {w: belief[w] * like[w] for w in WORLDS}
    z = sum(surviving.values())
    if z == 0:  # degenerate; should not happen with non-zero likelihoods
        return dict(belief)
    return {w: surviving[w] / z for w in WORLDS}


def update_all(belief: Belief, signals: List[str]) -> Belief:
    """Chain several evidence signals (section 4.6 -- posterior becomes prior)."""
    for s in signals:
        belief = bayes_update(belief, s)
    return belief


# --- expected loss (section 6.1) -------------------------------------------

def expected_loss(belief: Belief, action: str) -> float:
    """E[loss | action] = sum_world P(world) x cost(action, world)."""
    return sum(belief[w] * COST[action][w] for w in WORLDS)


def _best_action(belief: Belief, allowed: List[str]) -> str:
    return min(allowed, key=lambda a: expected_loss(belief, a))


# --- Policy A: full belief engine (sections 6.1-6.4) -----------------------

def decide_full(source: str, initial_signals: List[str],
                extra_signals: Optional[List[str]] = None) -> dict:
    """Full policy: expected-loss action, with BUY (capped) and FLAG.

    `initial_signals` are the clues the agent has before any buy.
    `extra_signals` are what a BUY reveals, consumed one per buy (section 4.6).
    """
    extra_signals = list(extra_signals or [])
    belief = prior_belief(source)
    belief = update_all(belief, initial_signals)
    buys = 0
    bought: List[str] = []

    while True:
        # 1. VOI-zero pre-filter (section 6.3): if missing/garbled dominate, no
        #    sound value to resolve -> do not buy; take the terminal min-loss.
        if belief["missing"] + belief["garbled"] >= 0.90:
            action = _best_action(belief, ["REJECT", "FLAG"])
            return _result(action, belief, buys, bought)

        # 2. Threshold met -> ACCEPT immediately (section 6.2).
        if belief["correct"] >= ACCEPT_THRESHOLD:
            return _result("ACCEPT", belief, buys, bought)

        # 3. Compare terminal actions vs. buying.
        terminal = _best_action(belief, ["ACCEPT", "REPAIR", "REJECT"])
        terminal_loss = expected_loss(belief, terminal)
        flag_loss = COST["FLAG"]["correct"]  # flat = 2

        # If a terminal action is already clearly cheap, act.
        if terminal_loss <= flag_loss and belief["correct"] >= ACCEPT_THRESHOLD:
            return _result(terminal, belief, buys, bought)

        # 4. Buy if we still have budget AND a clue to buy AND buying could help.
        if buys < MAX_BUYS and extra_signals:
            # cost-cap stop rule (section 6.3): never spend more than FLAG (=2).
            signal = extra_signals.pop(0)
            belief = bayes_update(belief, signal)
            buys += 1
            bought.append(signal)
            continue

        # 5. Out of budget / no more evidence: pick the cheapest of the terminal
        #    actions vs. FLAG. FLAG (2) is the safety net for unresolved doubt.
        best_terminal = _best_action(belief, ["ACCEPT", "REPAIR", "REJECT"])
        if expected_loss(belief, best_terminal) < flag_loss:
            return _result(best_terminal, belief, buys, bought)
        return _result("FLAG", belief, buys, bought)


# --- Policy B: autonomous, no human, no buy --------------------------------

def decide_autonomous(source: str, initial_signals: List[str],
                       extra_signals: Optional[List[str]] = None) -> dict:
    """No FLAG, no BUY. Must commit to ACCEPT / REPAIR / REJECT.

    This isolates the value of the human-in-the-loop + information-buying: the
    agent is forced to guess on ambiguous cases, so REJECT tends to become its
    safety valve rather than risk a cost-20 wrong ACCEPT.
    """
    belief = prior_belief(source)
    belief = update_all(belief, initial_signals)
    action = _best_action(belief, TERMINAL_ACTIONS)
    return _result(action, belief, buys=0, bought=[])


# --- Baseline: calibrated score + threshold (the Reddit "dumb" policy) ------

def decide_baseline(source: str, initial_signals: List[str],
                    extra_signals: Optional[List[str]] = None) -> dict:
    """A single confidence score P(correct) with two thresholds. No worlds, no
    per-world repairs -- exactly the "score + threshold" strawman PLBjt described.

      P(correct) >= accept_hi          -> ACCEPT
      P(correct) <= reject_lo          -> REJECT
      otherwise                        -> FLAG (send to a human queue)

    It reuses the same belief P(correct) so the comparison is apples-to-apples;
    the point is that it ignores WHICH failure world, so it cannot REPAIR or pick
    a targeted next probe.
    """
    accept_hi = 0.90
    reject_lo = 0.40
    belief = prior_belief(source)
    belief = update_all(belief, initial_signals)
    p_correct = belief["correct"]
    if p_correct >= accept_hi:
        action = "ACCEPT"
    elif p_correct <= reject_lo:
        action = "REJECT"
    else:
        action = "FLAG"
    return _result(action, belief, buys=0, bought=[])


# --- helpers ----------------------------------------------------------------

def _result(action: str, belief: Belief, buys: int, bought: List[str]) -> dict:
    return {
        "action": action,
        "belief": {w: round(belief[w], 4) for w in WORLDS},
        "p_correct": round(belief["correct"], 4),
        "buys": buys,
        "bought": bought,
    }


POLICIES = {
    "full": decide_full,
    "autonomous": decide_autonomous,
    "baseline": decide_baseline,
}

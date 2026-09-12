# Information-Decision Record (Week-2, Section: information layer)

A reproducible audit trail for one concrete **information** decision: given a
doubtful field, *which clue does the agent buy next*, and *when does it stop buying
and act*? Where the `probability-decision-record.md` audits a belief→action step,
this record audits the **buy / stop** step that sits in front of it, decided by
**expected information per unit cost** and **value of information (VOI)**, not by a
flat budget cap.

All numbers reuse the worked 160 GB RAM case and reproduce §9–§12 of
`belief-engine-decision-model.md`. Every quantity is computed from the §4.3 posterior
and the §5.4 cost matrix by a stdlib-only script — no new assumptions are introduced
here beyond the labelled per-clue likelihoods in §10.1.

---

## Case under audit

- **Field:** `ram_gb`, scraped value **160**, phone listing (mid-reliability source).
- **State at decision time:** the agent already applied the free clues and the
  *out-of-support* check (§4). Its belief is the **post-oos posterior**:

  | correct | wrong_product | unit_error | typo | missing | garbled |
  |:--:|:--:|:--:|:--:|:--:|:--:|
  | 0.089 | 0.134 | 0.357 | 0.402 | 0.009 | 0.009 |

- **Doubt = entropy = 1.881 bits** (of a 2.585-bit ceiling for 6 worlds). The leader
  is `typo` (0.402) but three error worlds are live — nowhere near a terminal call.

---

## Version metadata (reproducibility)

- Posterior source: `belief-engine-decision-model.md` §4.3.
- Cost matrix: §5.4 (ACCEPT/REPAIR/BUY=1/FLAG=2/REJECT).
- Clue likelihoods: §10.1 (author assumptions, labelled).
- Arithmetic: `python3` stdlib (`math.log2`, `math.erf`); entropy `H=−Σp·log2 p`,
  VOI `= E[loss now] − E[loss after clue]` with the post-clue loss averaged over
  outcomes. Same inputs → same result.

---

## Step 1 — Which clue is worth buying next? (expected bits per unit cost)

Three costed clues are available (§2.1 Tier B). Ranked by **expected** information
gain (not the after-the-fact number) divided by cost:

| Clue | Cost | E[info gain] | **Bits / cost** | Rank (per-cost) |
|------|:--:|:--:|:--:|:--:|
| Manufacturer proxy = "16 GB" | 2 | 0.250 bits (most) | 0.125 | 2 |
| Cross-source panel = "16 GB" | 1 | 0.135 bits | **0.135** | 🥇 1 |
| Reference catalogue (stale) | 1 | 0.039 bits | 0.039 | 3 |

**Reading.** The manufacturer proxy carries the most *raw* information (0.250 bits)
but the cross-source panel wins **per rupee** (0.135 > 0.125) — the raw-bits and
bits-per-cost rankings *disagree*, so "most informative" and "best buy" are not the
same clue. The reference catalogue is almost worthless here (0.039 bits): the specific
catalogue on hand is scraped/stale, so a "match" barely discriminates the worlds.
*(All three likelihood rows were reasoned out world-by-world by the author; see
`WORKING-CONTEXT.md` §W2.)*

---

## Step 2 — Should we buy it at all? (value of information)

Bits are not the stop test; **expected loss** is. Terminal-action costs at the
current belief:

| Terminal action now | E[loss] |
|---------------------|:--:|
| **FLAG** | **2.00** ← cheapest |
| REJECT | 4.21 |
| REPAIR | 4.50 |
| ACCEPT | 18.22 |

Now price **every** clue — including the *most informative* one (manufacturer,
0.250 bits). For each, the cheapest terminal action in **both** outcome branches is
still **FLAG @ 2.00**:

| Clue (bits, cost) | if positive | if negative | E[loss after] | VOI | net VOI |
|---|:--:|:--:|:--:|:--:|:--:|
| Manufacturer (0.250, 2) | FLAG @ 2.00 | FLAG @ 2.00 | 2.00 | 0.00 | −2.00 |
| Cross-source (0.135, 1) | FLAG @ 2.00 | FLAG @ 2.00 | 2.00 | 0.00 | −1.00 |
| Reference (0.039, 1) | FLAG @ 2.00 | FLAG @ 2.00 | 2.00 | 0.00 | −1.00 |

> **Every clue: VOI = 0.  Net VOI < 0.**

**Decision: DO NOT BUY. FLAG-FOR-HUMAN now.**

Even the *most informative* clue (0.250 bits) has **zero decision value**: whatever it
returns, FLAG @ 2 stays cheapest. The reason (reasoned out before computing): a
positive manufacturer result only lifts `unit_error` to ≈0.55, and REPAIR-ing on 0.55
eats the cost-18 penalty ~45% of the time — worse than a guaranteed FLAG = 2. **Bits ≠
decision value.**

---

## Contrast with the Week-1 rule (why this record exists)

Week-1 §6.3 used a **flat 2-buy cap**: uncertain + `P(correct) < 95%` → BUY, up to
twice, then FLAG. On this case that heuristic **spends at least one buy before
flagging**. The VOI rule flags immediately and **saves that spend** — a genuinely
different decision. The cap could not tell a value-adding buy from a wasted one;
VOI can, because it compares expected *loss*, not just information.

VOI is **not** "never buy". Sweeping `P(correct)` toward the ACCEPT/FLAG frontier, a
cheap confirming clue (cost 1) becomes VOI-positive exactly where it can tip ACCEPT
below FLAG (matches model §11.2):

| `P(correct)` | Best terminal now | Net VOI of clue | Decision |
|:--:|:--:|:--:|:--:|
| 0.40 (this case) | FLAG @ 2.00 | −1.00 | flag now |
| 0.86 | FLAG @ 2.00 | +0.12 | **buy** |
| 0.90 | ACCEPT @ 2.00 | +0.34 | **buy** |
| 0.92 | ACCEPT @ 1.60 | +0.05 | **buy** |

---

## What this decision exposed (honest note)

FLAG's flat **2** is a very strong ceiling, so under this exact cost matrix
VOI-positive buys live only in a thin band near the ACCEPT frontier — meaning the
belief engine should buy **far less** than Week-1 assumed. Either human review really
is that cheap, or our `FLAG = 2` is too optimistic (it ignores human error, latency,
and the cost of a 57%-review-rate; see `belief-engine-decision-model.md` §8 open
question 8). The VOI analysis turned a buried modelling assumption into a visible
driver of the whole buy policy — which is the point of writing the record.

**A tested (and falsified) fix.** The natural next thought — "then just make the human
expensive and buying will revive" — was tested and is **false**: raising FLAG from 2
to 15 lifts VOI off zero but it **plateaus** (manufacturer 0.38, cross-source 0.23) and
never clears the clue cost, because once FLAG ≥ 5 the fallback simply switches to
REJECT @ 4.21 (capped by the matrix, independent of FLAG). On a high-entropy case,
buying fails not because the human is cheap but because **no single clue can
concentrate belief enough to escape into a cheaper action** (see
`belief-engine-decision-model.md` §13.1).

*The full sequential version (buy → re-evaluate VOI → buy again) is an
optimal-stopping / SPRT problem; the one-step VOI above is its greedy first move,
scoped for this deliverable.*

# Product Data Normalization Belief Engine — Weeks 1–2 combined (AI-Native Engineering, Cohort 3)

A **thinking-first belief-engine** that decides, per scraped product-spec field,
whether a value is safe to publish — when the true canonical specification is never
observed at decision time. Built in the style of the course "The Belief Engine."

**Week 2 adds an information layer** on top of the Week-1 belief+cost engine: it
measures doubt in **bits** (entropy), ranks which clue to buy next by **expected
information gain per unit cost**, and replaces the flat 2-buy cap with a true
**value-of-information** stop rule. See model §9–§13 and preprint §7.

## Problem (one sentence)
The agent observes a scraped product field value (e.g. `ram_gb`, `storage_gb`,
`weight_g`) and must **ACCEPT / REPAIR / BUY-more-evidence / FLAG-FOR-HUMAN / REJECT**
it, because whether the value matches the product's true canonical spec is unknown.
Domain: consumer electronics (phones/laptops). Granularity: one decision per field.

## The idea in four moves
1. **Six MECE hidden "worlds"** produce a value: `correct / unit_error / wrong_product
   / typo / missing / garbled`.
2. **Belief** — start from a source-reliability prior (manufacturer / mid-retail /
   sketchy), update with Bayes on cheap evidence signals (out-of-support,
   unit-convertible, cross-source agree/disagree, empty, junk).
3. **Cost** — an asymmetric matrix where publishing a wrong value (20) dwarfs flagging
   (2) or buying evidence (1).
4. **Policy** — take the action with the **smallest expected loss**; ACCEPT only above
   a cost-derived confidence (Chow's reject-option), buy evidence under a budget cap,
   otherwise flag to a human.

## Honest headline result (N = 40 labelled cases)
The full belief policy has the lowest average cost (**2.30** vs baseline **3.10**;
paired Wilcoxon *p* ≈ 0.015) — **but the win is narrow and bought by escalation, not by
being smarter:**
- median per-case cost difference is **0** (only 9 of 40 cases differ);
- all three policies commit the **same 2 catastrophic wrong-publishes**;
- the full policy routes **57.5%** of cases to a human;
- the top confidence bin (P ≥ 0.95) is only **~60% empirically correct** — a
  miscalibration that, if real, *inverts* the ACCEPT decision.

This is presented as a **calibrated way of thinking**, not a production system. See the
preprint (`paper/preprint.pdf`) Results/Limitations sections for the full honest
accounting, and §7 for the Week-2 information layer.

## Week-2 information-layer findings (same worked `160 GB` case)
- **Doubt in bits:** prior entropy **2.12 bits** → after the out-of-support clue only
  **1.88 bits**. The clue *flips the leading world* (`correct`→`typo`) yet barely cuts
  doubt — changing the top pick ≠ reducing uncertainty.
- **Which clue to buy:** the manufacturer proxy is most *informative* (0.250 bits) but
  the cheaper cross-source panel wins on **bits-per-cost** (0.135 vs 0.125) — raw-bits
  and per-cost rankings *disagree*; the stale reference catalogue is nearly worthless
  (0.039 bits).
- **When to stop (true VOI):** on this case **every clue has VOI = 0** (FLAG@2
  dominates all branches) → the agent should **flag now, not buy** — a *different*
  decision from Week-1's flat cap.
- **A falsified hypothesis:** we predicted that making the human expensive would revive
  buying. Tested it — **false**: as FLAG rises 2→15, VOI plateaus (0.38/0.23) and never
  clears the clue cost, because the fallback just switches FLAG→REJECT. On a foggy case,
  no single clue can concentrate belief enough to be worth buying.
- *All clue likelihoods, costs, and this experiment were reasoned out by the author
  step-by-step; see `WORKING-CONTEXT.md` §W2.*

## Repository map
| Path | What it is |
|------|------------|
| `decisions/belief-engine-decision-model.md` | The live thinking artifact — worlds, priors, Bayesian update, cost model, policy, experiment table, failure analysis. **Center of gravity.** |
| `decisions/probability-decision-record.md` | One belief→action decision traced end-to-end with an audit-data row (the `160 GB` case; policy 1.0 → 1.1 flip). |
| `decisions/information-decision-record.md` | **(Week 2)** One information decision traced: which clue to buy next (bits-per-cost) and when to stop (true VOI), on the `160 GB` case. |
| `src/` | Runnable agent: `domain.py` (constants from the model), `agent.py` (Bayes + 3 policies), `generate_data.py`, `evaluate.py`, and `information.py` (Week-2 entropy / bits-per-cost / true VOI, reproducing model §9–§13). Pure stdlib. |
| `data/cases.jsonl` | 40 labelled evaluation cases (labels hidden at decision time). |
| `results/` | `metrics.json`, `report.md`, per-policy decision logs, and `README.md` reading the numbers. |
| `paper/` | `preprint.tex` + `references.bib` → `preprint.pdf` (combined 13-section paper incl. the Week-2 information layer §7, plus a 20-question appendix). |
| `research-file.md` | Groundwork: problem, terms, search queries, candidate communities, papers/datasets. |
| `discussion-record.md` | Human-discussion strategy + the **real** discussions log and how each changed the design. |
| `review-record.md` | Three adversarial AI reviews (practitioner / probability / preprint) and the adjudication of every comment. |
| `social/` | `linkedin-post.md` + `x-thread.md` drafts. |
| `WORKING-CONTEXT.md` | How this collaboration operates + a running step log + a concepts-learned glossary. |
| `PLAN.md` | The full step plan with status. |

## Reproduce
Requires Python 3.11+ (standard library only — no dependencies).

```bash
cd src
python3 generate_data.py   # writes ../data/cases.jsonl (deterministic, seed 20260830)
python3 evaluate.py        # writes ../results/{metrics.json,report.md,decisions_*.jsonl}
python3 information.py     # prints the Week-2 entropy / bits-per-cost / VOI trace (model §9–§13)
```

Rebuild the preprint (needs a LaTeX engine; [tectonic](https://tectonic-typesetting.github.io/) recommended):

```bash
cd paper
tectonic preprint.tex      # writes preprint.pdf
```

## AI-use statement
See `AI-USE.md`. In short: an AI assistant (Claude, via the Cursor harness) was used as
a Socratic pair — it taught concepts, asked clarifying questions, and drafted files,
while the author owned every design decision. Three AI reviews were run in separate
sessions across different models and each comment was adjudicated. All conversations
and decisions are logged in `WORKING-CONTEXT.md` and `review-record.md`.

## Status
All deliverable steps complete except the *publishing* of the social posts (drafts
ready in `social/`) and any further real community engagement. See `PLAN.md` for the
step-by-step status and `docs`/completion checklist below.

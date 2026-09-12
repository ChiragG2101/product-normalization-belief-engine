# Probability and Decision Record (Section 10)

A reproducible audit trail for one concrete decision. It records the inputs, the
version metadata, the full belief chain (prior -> evidence -> likelihood ->
posterior), which policy threshold fired, and the action taken -- so the decision
is explainable ("why this action") and reproducible ("same versions -> same
result"). Numbers reuse the worked case in `belief-engine-decision-model.md`
(sections 4 and 6).

This record is deliberately told in two versions. Version 1.0 trusted cross-source
agreement as strong, independent evidence and confidently REPAIRed. A real Reddit
discussion (see `discussion-record.md`) pointed out that cross-source agreement is
not independent -- sites copy the same upstream feed -- which is failure mode F2 in
the decision model. Version 1.1 down-weights that correlated evidence, and the same
clue is no longer strong enough to justify a silent repair: the agent FLAGs for a
human instead. The discussion changed the decision. That is the point of the record.

---

## Case under audit

- **case_id:** `case-160gb-ramgb-mid-0001`
- **Field / value:** `ram_gb = "160 GB"` for a phone.
- **Source:** mid-reliability retail (uses the mid prior).
- **Hidden true world (revealed post hoc, for scoring only):** `typo`
  (`160 GB` is a dropped-digit slip of `16 GB`).

---

## Audit-data (the metadata that makes this reproducible)

The four version fields plus the movable support range. Rerunning with the same
values below must reproduce the same posteriors and action.

| Field | Value | Note |
|-------|-------|------|
| `timestamp` | 2026-08-29T20:45:00+05:30 | when the decision was made |
| `data_version` | `scrape-2026-08-29` | the scrape/dataset snapshot the value came from |
| `model_version` | `beliefs-1.0` | the prior board + likelihood tables (sections 3, 4) |
| `policy_version` | `policy-1.0` -> `policy-1.1` | thresholds + VOI rules (section 6); bumped mid-record (see below) |
| `support_range(ram_gb, phone)` | `[1, 24] GB` | the plausibility band used; a labelled assumption, not a fact |

Why `support_range` is logged as audit-data: it is an assumption that can be wrong
(failure mode F5, "stale support range"). If a genuinely new 32 GB phone ships, this
band moves, and logging it means an old decision can be re-explained against the band
that was actually in force at the time.

---

## Clue 1 -- the value reads out-of-support

- **Evidence:** support / plausibility check. Phone RAM tops out around ~24 GB, so
  `160 GB` is **OUT-OF-SUPPORT**.
- **Prior (mid source), P(world):** correct 0.50, unit_error 0.10, wrong_product
  0.15, typo 0.05, missing 0.10, garbled 0.10.
- **Likelihood P(out-of-support | world):** correct 0.02, typo 0.90, unit_error
  0.40, wrong_product 0.10, missing 0.01, garbled 0.01.

**Update (prior x likelihood, normalize):**

| World | prior | x L | surviving | posterior |
|-------|:---:|:---:|:---:|:---:|
| typo | 0.05 | 0.90 | 0.0450 | **0.402** |
| unit_error | 0.10 | 0.40 | 0.0400 | **0.357** |
| wrong_product | 0.15 | 0.10 | 0.0150 | **0.134** |
| correct | 0.50 | 0.02 | 0.0100 | **0.089** |
| missing | 0.10 | 0.01 | 0.0010 | **0.009** |
| garbled | 0.10 | 0.01 | 0.0010 | **0.009** |
| **total** | 1.00 | -- | 0.1120 | 1.000 |

**Policy check (section 6 cost matrix):** E[ACCEPT] ~= 0.911 x 20 ~= 18.2;
E[REPAIR] ~= 4.5; E[REJECT] ~= 4.0; E[FLAG] = 2.0; **E[BUY] = 1.0 (smallest)**.

- **Threshold fired:** none for a terminal action (P(correct)=8.9% is far below the
  95% ACCEPT threshold). Lowest expected loss is BUY.
- **Action after clue 1:** **BUY** more evidence (buy_count -> 1, under the cap of 2).
- **Why:** the value is implausible but a shocking clue cannot stampede a rare prior
  to certainty (base-rate discipline). unit_error/typo are only hypotheses; buying a
  second clue is worth more than any terminal action right now.

---

## Clue 2 -- cross-source agreement returns "16 GB"

The bought evidence: other retail sources list this field as `16 GB`. The posterior
from clue 1 now becomes the **prior for clue 2** (belief chaining -- today's
posterior is tomorrow's prior).

**Modeling note (which world does "16 GB" reward?).** The bad value `160 GB` and the
clue `16 GB` are *both already in GB*. Going `160 -> 16` is a dropped digit, i.e. a
**typo**, not a unit error. A unit error would surface as an MB-flavoured artifact
(e.g. `16000 MB`), which we did not see. So a clean `16 GB` clue argues *for* typo and
*against* unit_error. (This corrects an earlier draft that credited unit_error --
caught during the step-10 review.)

### Version 1.0 -- cross-source treated as STRONG, independent evidence

- **Likelihood P("16 GB" cross-source | world):** typo 0.90, unit_error 0.10,
  wrong_product 0.15, correct 0.05, missing 0.02, garbled 0.02.

| World | prior (=clue-1 post) | x L | surviving | posterior v1.0 |
|-------|:---:|:---:|:---:|:---:|
| typo | 0.402 | 0.90 | 0.36180 | **0.857** |
| unit_error | 0.357 | 0.10 | 0.03570 | **0.085** |
| wrong_product | 0.134 | 0.15 | 0.02010 | **0.048** |
| correct | 0.089 | 0.05 | 0.00445 | **0.011** |
| missing | 0.009 | 0.02 | 0.00018 | **0.000** |
| garbled | 0.009 | 0.02 | 0.00018 | **0.000** |
| **total** | 1.000 | -- | 0.42241 | 1.000 |

**Policy check (v1.0 posterior):**
- E[REPAIR] (`160`->`16`) ~= 0.011x18 + 0.857x4 + 0.085x0 + 0.048x8 + ~0
  ~= 0.20 + 3.43 + 0.38 ~= **~1.6**
- E[FLAG] = 2.0; E[REJECT] ~= 0.011x5 + 0.857x2 + 0.048x6 + 0.085x6 ~= **~2.8**;
  E[ACCEPT] ~= 0.989x20 ~= 19.8.
- **Smallest = REPAIR (~1.6).**

- **Threshold / rule fired:** expected-loss minimum is REPAIR, and it beats the FLAG
  floor (2.0); buy_count=1 is under the cap so no forced escalation.
- **Action (v1.0):** **REPAIR -> `16 GB`**, publish. Confident, decisive.

---

## Review event -- a discussion changes the model

**Trigger:** a practitioner on Reddit (r/WebScrapingInsider thread, logged in
`discussion-record.md`) responded to the post with:

> "I trust consistency with the rest of the product more than raw source agreement.
> 5 sites showing the same value isn't that useful if they're all copying the same
> feed."

This independently confirms **failure mode F2 (coordinated cross-source error)**: our
v1.0 likelihood treated cross-source agreement as *independent* evidence, but sources
copy the same upstream feed, so "several sites agree" is closer to **one** noisy
observation than to many. Treating correlated agreement as independent over-counts it
and can push a cheap, silent REPAIR that isn't actually well supported.

**Change made (provenance):** bump `policy_version` 1.0 -> 1.1 -- down-weight
correlated cross-source evidence (treat agreeing copies as roughly a single weak
source). No change to the prior board or the cost matrix; only the clue-2 likelihood
strength changes.

---

## Clue 2 re-evaluated -- Version 1.1 (down-weighted for correlation)

- **Likelihood P("16 GB" cross-source | world), discounted:** typo 0.45 (was 0.90),
  unit_error 0.10, wrong_product 0.15, correct 0.05, missing 0.02, garbled 0.02.
  (Only typo's strength is cut, since it was the world the correlated agreement was
  over-rewarding; the cut is ~to a third of the "excess" evidence power.)

| World | prior (=clue-1 post) | x L | surviving | posterior v1.1 |
|-------|:---:|:---:|:---:|:---:|
| typo | 0.402 | 0.45 | 0.18090 | **0.749** |
| unit_error | 0.357 | 0.10 | 0.03570 | **0.148** |
| wrong_product | 0.134 | 0.15 | 0.02010 | **0.083** |
| correct | 0.089 | 0.05 | 0.00445 | **0.018** |
| missing | 0.009 | 0.02 | 0.00018 | **0.001** |
| garbled | 0.009 | 0.02 | 0.00018 | **0.001** |
| **total** | 1.000 | -- | 0.24151 | 1.000 |

**Policy check (v1.1 posterior):**
- E[REPAIR] (`160`->`16`) ~= 0.018x18 + 0.749x4 + 0.148x0 + 0.083x8 + 0.002x12
  ~= 0.32 + 3.00 + 0.66 + 0.02 ~= **~4.0**
- **E[FLAG] = 2.0 (flat)**
- E[REJECT] ~= 0.018x5 + 0.749x2 + 0.148x6 + 0.083x6 ~= 0.09 + 1.50 + 0.89 + 0.50
  ~= **~3.0**
- E[ACCEPT] ~= 0.982x20 ~= 19.6; E[BUY] would be 1.0 but buy_count=1 and a second
  correlated fetch has low VOI (same feed) -> not worth it.
- **Smallest = FLAG (2.0).**

- **Threshold / rule fired:** no terminal action clears its cost floor -- REPAIR (~4.0)
  now *exceeds* the FLAG floor (2.0) because the repair is no longer well supported.
  VOI of another correlated buy ~ 0, so we do not spend the second buy.
- **Action (v1.1):** **FLAG-FOR-HUMAN.**

**What flipped and why:** the belief barely moved (typo 85.7% -> 74.9%), but that was
enough to cross the REPAIR-vs-FLAG boundary. A silent repair is only worth it when the
evidence is strong; once the correlated clue is honestly discounted, the cheapest safe
move is a human check. **The discussion changed the action from REPAIR to FLAG.**

---

## The required transition, in one line (prior -> ... -> new action)

| Version | prior (P(typo)) | evidence | likelihood(typo) | posterior (P(typo)) | threshold / rule | action |
|---------|:---:|----------|:---:|:---:|------|--------|
| after clue 1 | 0.05 | out-of-support | 0.90 | 0.402 | min-loss = BUY (no accept threshold met) | **BUY** |
| clue 2, policy 1.0 | 0.402 | cross-source "16 GB" (trusted as independent) | 0.90 | 0.857 | min-loss = REPAIR < FLAG floor | **REPAIR -> 16 GB** |
| clue 2, policy 1.1 | 0.402 | same clue, **discounted for correlation** | 0.45 | 0.749 | REPAIR loss (4.0) > FLAG floor (2.0) | **FLAG-FOR-HUMAN** |

---

## Reproducibility statement

Re-running with `model_version = beliefs-1.0`, `policy_version = policy-1.1`,
`support_range(ram_gb, phone) = [1,24] GB`, the mid-source prior, and the two clues
above (out-of-support, then cross-source "16 GB") reproduces P(typo)=0.749 and the
action FLAG-FOR-HUMAN. Swapping `policy_version` back to `policy-1.0` reproduces the
REPAIR decision. All numbers trace to sections 3-6 of
`belief-engine-decision-model.md`; every likelihood and cost is a labelled author
assumption with a stated rationale, not a measured fact.

*Concept receipts (provenance, chaining, expected loss, VOI) live in
`WORKING-CONTEXT.md` section 6 (glossary).*

# Belief-Engine Decision Model — Product Data Normalization Agent

A thinking-first decision model for a per-field scraped-data normalization agent,
built in the style of the course "The Belief Engine" (Cohort 3, Week 1). It shows
how the agent holds several explanations open, updates belief with evidence, and
chooses an action by expected cost — with a human in the loop for the expensive
cases.

Sections fill in step by step. Numbers are owned by the author; assumptions are
labelled as assumptions with their source (provenance), never presented as fact.

---

## 0. Problem statement (assignment format)
> The agent observes a scraped product field value. It must **ACCEPT**,
> **REPAIR**, **buy more evidence** (re-scrape / query manufacturer),
> **FLAG-FOR-HUMAN**, or **REJECT** it because whether the value matches the
> product's true canonical specification is not known.

- **Domain:** consumer electronics (phones/laptops).
- **Granularity:** one decision per scraped field (e.g. `ram_gb`, `storage_gb`,
  `weight_g`, `screen_size_in`, `battery_mah`).
- **Hidden outcome:** which of several "worlds" produced this value (see §1).

### 0.1 Week-2 research question (information layer)

Week 1 established *what* the agent believes and *which action* minimises expected
loss. Week 2 narrows to the question the belief engine never actually answered:

> **Given a doubtful field, which cheap clue should the agent buy next — and when
> should it stop buying and act — if we choose by *expected information per unit
> cost* rather than by a flat budget cap?**

Concretely we (a) measure the agent's doubt in **bits** (entropy) before and after
evidence; (b) rank candidate clues by **expected information gain ÷ cost**
(bits-per-rupee), being careful to use the *expected* gain before the clue is seen,
not the gain we observe after a specific outcome; and (c) replace the Week-1 flat
"2-buy cap" with an explicit **value-of-information (VOI)** stop rule derived from
the same asymmetric cost matrix. The locked worked example is the **160 GB RAM**
case from §4.

*Readiness roadmap (from the `week2-readiness` skill) is recorded in
`WORKING-CONTEXT.md` §W2; the per-step teaching ritual is unchanged.*

---

## 1. Possible worlds (the hidden states) — MECE

The hidden reality is *one* of the worlds below. They are **mutually exclusive**
at the level of what actually happened, and **collectively exhaustive** (the
`garbled` box is the "something else" catch-all). When the agent cannot tell two
worlds apart from the value alone, that is *belief uncertainty* — it splits its
100 tokens across the live worlds; it does **not** merge the boxes.

Classification tie-breaker (so a case never sits in two boxes), applied in order:
1. Can't parse the value as this field at all -> **garbled**.
2. Value is empty / null / placeholder-empty -> **missing**.
3. Value parses to a number -> decide among correct / unit_error / typo /
   wrong_product using the plausibility ("support") and unit-conversion tests.

| # | World | Definition (the *reality* that produced the value) | How it typically shows up |
|---|-------|----------------------------------------------------|---------------------------|
| 1 | **correct** | Value matches the true canonical spec for *this* product + field. | In-support, agrees with trusted sources. |
| 2 | **unit_error** | Correct magnitude, wrong unit. | Becomes plausible only after a unit conversion, e.g. `16000 MB` -> `16 GB`; `0.19 kg` -> `190 g`. *(Narrow by design: an AI review (Sec 11) noted a broader class of **measurement-definition errors** — net vs gross weight, screen diagonal vs width, advertised vs usable storage, nominal vs typical battery — which are semantic, not scale, transforms. Logged as future work in §8.)* |
| 3 | **wrong_product** | A valid, in-support value, but taken from a different product / variant / revision (includes **stale** = an older discontinued version's spec). | Looks perfectly normal in isolation; disagrees with the true product's other evidence. |
| 4 | **typo** | Transcription slip producing an off / out-of-support number. | `160 GB` RAM (impossible for a phone), `1660 g` for a `166 g` phone, swapped/extra/missing digit. |
| 5 | **missing** | Empty / null / placeholder-empty value. | `""`, `null`, `"-"` used as empty. |
| 6 | **garbled** | Present but unparseable as this field: encoding junk, HTML fragments, non-values. | `"N/A"`, `"8&nbsp;GB"`, `"see description"`, mojibake. |

**Boundary (explicitly out of scope):** deciding whether the scraped text is even
the *right kind* of field (a "non-required value" that isn't this spec at all).
That is an upstream routing decision handled before this per-field agent. Noting
this keeps the problem "small and testable" (course guidance) and is itself an
honest "what it can't do" statement.

**Why typo and wrong_product are separate boxes (decision-relevance test):**
from the value alone we often cannot tell them apart, but our *actions* could
differ — a `wrong_product` value may be recoverable by locating the correct
SKU/revision, whereas a `typo` is noise to be repaired or rejected. A distinction
that could change what we do earns its own box (Chapter 4 information-gain logic).

*Concept receipts for this section live in `WORKING-CONTEXT.md` §6 (glossary).*

---

## 2. Observations vs hidden outcome (three layers)

We keep three layers strictly apart (Chapter 1, "The Email Behind the Curtain"):

- **Layer 1 — hidden reality:** the one true story of what produced this value.
  Exactly one of the six worlds in §1 is true. The agent **never observes this
  layer** at decision time; if it could, there would be no problem to solve.
- **Layer 2 — observations:** the clues that actually reach the agent. Clues are
  *caused by* the reality but are **not** the reality — any single clue can
  mislead.
- **Layer 3 — belief:** our token split across the six worlds given the clues
  (e.g. `70 correct / 20 wrong_product / 10 typo`). This is the only layer we
  build and control. Belief updates **only through observations** (sets up §3–§4).

### 2.1 What the agent observes (Layer 2), in two tiers

The clues split into what we **already hold for free** at decision time vs. what
we must **spend to acquire** (a costed action — Chapter 5, "information is not
free"). This split drives the info-buying actions in §6.

**Tier A — already-have (free, arrives with the scraped record):**

| Clue | Why it is only a clue (not the answer) |
|------|----------------------------------------|
| The scraped **value** itself (e.g. `"16 GB"`) | The thing under suspicion; can be any of the six worlds. |
| **Source website / full URL** | Signals source reliability; a trusted domain shifts tokens but never proves correctness. |
| **Feature category** (e.g. RAM vs. storage) | Fixes which *support* (allowed range) applies; helps place the value, doesn't verify it. |
| **SKU / model code** | A join key to *other* sources — useful only once joined (see Tier B). |
| **Product (marketing) name** | Feels like it reveals the truth (often contains "16GB"), but is itself a scraped string that can be wrong, rounded, or from the wrong variant. A clue, not the spec. |
| **Launch date** | Bounds plausibility (era-appropriate specs); weak on its own. |
| **Scrape timestamp** | Flags staleness; contextual only. |

**Tier B — go-buy (costed; requires a fresh fetch):**

| Clue | How it is acquired | Cost |
|------|--------------------|------|
| **Cross-source agreement** — what other sites report for this same field | Re-scrape / join by SKU across sources | a fetch per source |
| **Manufacturer spec-page value** — a *proxy* for the canonical spec | Query the brand's official page / API | a fetch + parse |
| **Reference-dataset lookup** | Match against a curated catalogue | a lookup |

### 2.2 The canonical spec is never observed — only a proxy is

Critical distinction we commit to: the **true canonical spec is Layer 1** and is
never an observation. What the agent can buy is a **high-trust *proxy*** for it
(e.g. "the manufacturer page *says* 16 GB"). That proxy is still a **Layer-2
clue** — very reliable, but able to be wrong (spec pages have errors, list the
wrong variant, or are cached/stale). Keeping this gap open is what prevents
overconfidence: even after buying the manufacturer value, belief may concentrate
sharply but never collapses to certainty.

### 2.3 What a human observes that the agent cannot (assignment §12)

A human reviewer perceives evidence that is structurally outside the per-field
agent's reach: the **product image**, the **full rendered page context**, whether
the **brand / product line even plausibly exists**, and general **domain
intuition**. This is exactly why **FLAG-FOR-HUMAN** is a real action — we escalate
when the decision hinges on evidence only a human can see.

*Concept receipts for this section live in `WORKING-CONTEXT.md` §6 (glossary).*

## 3. Counted prior / starting belief board

The **prior** is our token split across the six worlds *before* we look closely at
this specific value — the base rate (Chapter 2, "The Base-Rate Trap"). It is the
floor the evidence must lift *from* (§4), not something evidence erases. Two
honesty rules: the board sums to 100, and every number carries a **receipt**.

### 3.1 The prior depends on source reliability (three boards)

Source reliability is itself a Tier-A clue (§2.1), so the starting board differs
by source. We keep **three priors** and pick one based on the record's source.

| World | Manufacturer page | Mid-reliability retail | Sketchy aggregator |
|-------|:---:|:---:|:---:|
| **correct** | 80 | 50 | 25 |
| **wrong_product** | 6 | 15 | 20 |
| **unit_error** | 4 | 10 | 15 |
| **typo** | 3 | 5 | 10 |
| **missing** | 4 | 10 | 15 |
| **garbled** | 3 | 10 | 15 |
| **sum** | **100** | **100** | **100** |

Direction of shift (author's committed reasoning): moving from mid → manufacturer,
tokens flow *toward* `correct` and away from the error worlds; moving mid →
sketchy, `correct` drops sharply and every error world swells.

### 3.2 Receipts (provenance)

- **Type:** *stated assumption, informed by the author's experience browsing major
  B2C retail sites* (Amazon, Flipkart, Vijay Sales, Croma). **Not** a counted
  labelled dataset — labelled as an assumption on purpose, not a "guess wearing a
  lab coat."
- **These are *weakly-informative* priors** (not non-informative) — a framing
  suggested by a practitioner in the r/AskStatistics discussion. They are informative
  enough to rule out the absurd (a non-informative prior would happily believe a phone
  has "100 ft of RAM"; ours, via the support range, caps RAM at ~1–24 GB) but not so
  strong they override real evidence. Honest limitation: **there is no general way to
  prove a strong prior is *justified*** (a standard objection to Bayesian methods);
  we mitigate by plotting prior/likelihood/posterior to see which is pulling, and by
  calibrating against audited outcomes over time (see §8).
- **How strongly does evidence dominate? Less than one might hope (AI probability
  review, Sec 11).** It is tempting to say "evidence washes the prior out once it's
  strong." That is only true in the *limit of several strong, independent signals*.
  Our own §4 worked case is a counterexample to the strong reading: after a single
  strong signal (`P(oos|typo)=0.90` vs `P(oos|correct)=0.02`, a 45:1 likelihood
  ratio) `correct` still only fell to 0.089 and `typo` only rose to 0.402 — the prior
  is *still visibly steering* the ranking (`unit_error` at 0.357 is neck-and-neck with
  `typo` on prior mass alone). Honest statement: **with a single strong signal the
  prior still matters a lot; it only washes out after several strong signals — and
  because our signals aren't independent (§4.6), that washout is slower than it looks.**
- **Cheap, label-free prior calibration (AI probability review, Sec 11) — a
  prior-predictive check.** The normaliser `P(clue) = Σ prior×likelihood` (the 0.112
  denominator in §4) is the model's *predicted* rate of seeing that evidence. So we can
  sanity-check the priors with **no labels**: compare predicted evidence-frequencies
  (rate of out-of-support values, empties, cross-source disagreement) against the
  *observed* rates in a cheap unlabelled scrape. If the priors predict 11%
  out-of-support and we observe 2%, they're miscalibrated — no labelled dataset
  required. This is stronger than "plot prior vs posterior" and is the calibration path
  we'd add first.
- **Mid-reliability board is the anchor.** The other two boards are the author's
  reasoned shifts from it (per §3.1 direction), not independent counts.
- **Why `correct = 50` (mid), not 30:** on B2C listings, core spec fields
  (RAM/storage) are usually *filled and roughly right* — that is the point of the
  listing. An initial `correct = 30` was revised up after re-examining the same
  receipt; it would have implied ~70% of values are flawed before even looking,
  an over-suspicious prior with real downstream cost.
- **Why `missing = 10` (mid), not 30:** revised down for the same reason — empty
  core-spec fields are the exception on these sites, not ~1-in-3.
- **Least-certain numbers (honest flag):** the manufacturer `correct = 80` (not
  higher, because even official pages carry the wrong-variant / stale risk from
  §2.2) and the sketchy split (widest guess — least first-hand experience).

### 3.3 Guard against the base-rate trap

A striking value (e.g. `160 GB` phone RAM) must **not** stampede the board (e.g.
"95 on typo") on its own. "Striking" is a statement about the *likelihood* (§4),
which must be **combined with** this prior, never allowed to overwrite it. A high
source-reliability prior legitimately keeps other worlds alive — the odd value
could be `wrong_product` (right value, wrong spec mapping) or a world we have no
clue about yet. Skipping the prior produces confident nonsense; this is exactly
the Chapter 2 trap.

*Concept receipts for this section live in `WORKING-CONTEXT.md` §6 (glossary).*

## 4. Evidence, likelihoods, and the Bayesian update (worked case)

This is the engine: a clue arrives and *moves* the prior board (§3) into a new
board. The move is **prior × likelihood, then normalize** (Chapter 2, the same
machine as the disease-test story). We work one concrete case end to end.

### 4.1 The case (locked, reproducible)

- **Source:** mid-reliability retail → use the **mid prior** from §3.1.
- **Field / value:** `ram_gb = "160 GB"` for a phone.
- **Evidence signal:** a **support / plausibility check** (§1). Phone RAM tops out
  around ~24 GB today, so `160 GB` reads **OUT-OF-SUPPORT**. That single reading
  is the clue we update on.

### 4.2 The likelihoods — `P(out-of-support | world)`

The **likelihood** is the backwards question: *if this world were the true
reality, how naturally would it produce an out-of-support value?* Answered one
world at a time (each is 0–1; they need **not** sum to anything — they are not a
budget, unlike the prior). *(The AI probability review, Sec 11, confirmed this is the
right object and a common point of confusion: `P(oos | world)` is a per-world
sampling probability, not a distribution over worlds — summing across worlds would be
a category error.)*

**Rigor nit to enforce (AI probability review, Sec 11).** This table only defines
`P(oos | world)`; for the binary support test the "in-support" case implicitly uses
`P(is | world) = 1 − P(oos | world)`, which is fine. But the moment a signal has **>2
outcomes** (e.g. cross-source ∈ {agree, disagree, absent}), the conditional
distribution must **sum to 1 over the evidence outcomes for a fixed world** (not over
worlds). Otherwise an "absent" outcome silently leaks probability mass. The code
(`src/domain.py`) must enforce this for any multi-valued signal.

| World | `P(oos \| world)` | Author's reasoning |
|-------|:---:|--------------------|
| correct | 0.02 | A correct value sits *inside* support by definition; out-of-support almost never. |
| typo | 0.90 | A transcription slip (extra digit, etc.) very often lands outside the plausible range. |
| unit_error | 0.40 | Genuinely possible (`16000 MB`→odd raw), but `160` raw is an unusual unit-error footprint; more than wrong/correct, not dominant. |
| wrong_product | 0.10 | A value copied from *another real* phone is usually still a *normal* number → rarely out-of-support. |
| missing | 0.01 | We received a *parsed* value, so "empty" ≈ ruled out (kept at 0.01, not 0, on principle). |
| garbled | 0.01 | Same — a clean parseable number is essentially not unparseable junk. |

### 4.3 The update — token view (multiply, then re-total)

| World | Prior | × Likelihood | = Surviving | → Posterior (tokens) |
|-------|:---:|:---:|:---:|:---:|
| typo | 5 | 0.90 | 4.50 | **40.2** |
| unit_error | 10 | 0.40 | 4.00 | **35.7** |
| wrong_product | 15 | 0.10 | 1.50 | **13.4** |
| correct | 50 | 0.02 | 1.00 | **8.9** |
| missing | 10 | 0.01 | 0.10 | **0.9** |
| garbled | 10 | 0.01 | 0.10 | **0.9** |
| **total** | 100 | — | **11.20** | **100.0** |

Re-total: each surviving pile ÷ 11.20 × 100.

### 4.4 The update — Bayes formula (same numbers, as probabilities)

`posterior(world) = prior × likelihood / Σ(prior × likelihood)`, priors as /100:

- Numerators: typo `0.05×0.90=0.045`, unit_error `0.10×0.40=0.040`,
  wrong_product `0.15×0.10=0.015`, correct `0.50×0.02=0.010`,
  missing `0.10×0.01=0.001`, garbled `0.10×0.01=0.001`.
- Denominator `P(clue) = Σ = 0.112` (this is the "normalize" / re-total term).
- Posteriors: **typo 0.402, unit_error 0.357, wrong_product 0.134, correct 0.089,
  missing 0.009, garbled 0.009.** Identical to §4.3. ✓

### 4.5 What the update tells us (reading the result)

1. **typo won (5 → 40)** because it explains the clue best — the clue rewarded it.
2. **But it did NOT run to 95.** typo was rare to start with, so it lands ~40, not
   ~95 — the base-rate trap defeated *mechanically*, not by willpower (cf. cancer
   staying at 1% in the disease-test story).
3. **unit_error surged (10 → 36):** an actionable signal — "before calling this a
   typo, check whether it's `16000 MB` misread." The model surfaces a hypothesis
   the eye would miss.
4. **correct collapsed (50 → 9)** — correct values shouldn't be out-of-support —
   but keeps a sliver (support range could be wrong, or a genuinely odd product).
5. **missing / garbled ≈ 1** each, since a parseable value was received.

### 4.6 Chaining (what pulls tokens back toward correct)

Belief updates compose: this posterior becomes the prior for the *next* clue. A
second clue — buying the manufacturer proxy (§2.1 Tier B) or cross-source
agreement near `160` — would run another Bayes update on this board and could pull
tokens back toward `correct` / `wrong_product`. This chaining is the whole engine
and feeds the policy in §6.

**Assumption we are smuggling in — conditional independence (flagged by the AI
probability review, Sec 11).** Multiplying likelihoods sequentially (clue 1, then
clue 2) is only valid if the signals are **conditionally independent given the
world**:

> `P(e₁, e₂ | world) = P(e₁ | world) · P(e₂ | world)`

We never stated this, but the chaining asserts it — and for *our* signals it is
questionable. `out-of-support` and `cross-source-disagreement` are **not**
independent given `typo`: a typo that pushes a value out of its plausible range will
*also* tend to make it disagree with other sources — one latent cause, two signals.
Chaining them double-counts that cause and **over-concentrates** the posterior
(over-confidence). This is the *general* form of the correlated-agreement worry in
§8 (cross-source copying is just one instance of the same violation), and it is the
most likely mechanistic root cause of the top-confidence-bin over-confidence seen in
the Step-11 calibration table. Honest fixes (future work, §8.3): assert + defend
independence per signal pair, model a **joint likelihood** for correlated signal
groups, or apply a naive-Bayes-style **weight-of-evidence discount** (a temperature
< 1 on chained log-likelihoods, exactly what text classifiers use because their
features aren't independent either). For this Week-1 prototype the chaining is kept
as-is and the assumption is now stated openly rather than hidden.

*Concept receipts for this section live in `WORKING-CONTEXT.md` §6 (glossary).*

## 5. Events, random variables, and the cost table

We now price mistakes. A moving belief board (§4) is useless for *deciding* until
we know what being wrong costs — and those costs are **asymmetric** (Chapter 0,
"The 92% Lie": not all errors are equal; name who pays). This table is the price
list the policy (§6) runs on.

### 5.1 The core random variable (the event)

Stakeholders don't act on six worlds; they act on a yes/no question. Our core
random variable:

> **`safe_to_publish` = "Is this value safe to publish as-is?"**
> → **YES** only for `correct`; **NO** for the five flawed worlds.

**Stakeholder / cost owner:** the **retailer** publishing the data — they bear
returns and reputation damage when wrong specs go live. (The end customer also
pays, by buying on wrong info, but the retailer internalizes it, which is why
they fund the fix.) A secondary event, `recoverable_by_repair` (true mainly for
`unit_error` and some `wrong_product`), motivates REPAIR vs. REJECT in §6.

### 5.2 The actions

- **ACCEPT** — publish as-is.
- **REPAIR** — transform then publish (e.g. `16000 MB` → `16 GB`).
- **BUY** — buy more evidence (re-scrape / manufacturer proxy) before deciding.
- **FLAG-FOR-HUMAN** — send to a human reviewer.
- **REJECT** — drop the value (publish nothing for this field).

### 5.3 Relative pain units (author's reasoned assumptions)

Cheapest mistake = **1 unit**; worst = **20 units** (a conservative floor — real
ratio may be higher). Ordering committed by the author on the principle *"whatever
ends up publishing wrong data is most expensive."*

| Mistake (action wrong for the true world) | Pain | Why |
|-------------------------------------------|:---:|-----|
| BUY when not needed | 1 | a wasted fetch (the anchor) |
| FLAG a correct value | 2 | a few minutes of wasted human review |
| REJECT a correct value | 5 | good data dropped, but **no lie published** |
| REPAIR that corrupts a correct value | 18 | **silently publishes a lie** — near the top |
| ACCEPT a flawed value | 20 | worst: wrong specs go live to customers |

### 5.4 The full cost matrix (action × true world)

Cost of taking each **action** (row) if the **true world** (column) turns out to
be that. `0` = right call, little/no harm. Values follow §5.3; intermediate cells
are interpolated on the same principle and labelled as author assumptions.

| Action ↓ / True world → | correct | unit_error | wrong_product | typo | missing | garbled |
|-------------------------|:---:|:---:|:---:|:---:|:---:|:---:|
| **ACCEPT** (publish as-is) | 0 | 20 | 20 | 20 | 20 | 20 |
| **REPAIR** (transform+publish) | 18 | 0 | 8 | 4 | 12 | 12 |
| **BUY** (get more evidence) | 1 | 1 | 1 | 1 | 1 | 1 |
| **FLAG** (human review) | 2 | 2 | 2 | 2 | 2 | 2 |
| **REJECT** (drop value) | 5 | 6 | 6 | 2 | 1 | 1 |

Reading the rows:
- **ACCEPT** is free if truly `correct`, but a flat 20 for any flawed world — it
  publishes the lie regardless of *which* flaw.
- **REPAIR** is free when the flaw is exactly repairable (`unit_error`), cheap on
  `typo` (often fixable/obvious), but a disastrous **18** if the value was
  actually `correct` (corrupts good data) and costly on `missing`/`garbled`
  (nothing sound to repair from).
- **BUY** is a flat small cost (1) — you never publish a lie by buying, you just
  pay a fetch. **FLAG** is a flat 2 (human time), safe but not free.
- **REJECT** drops the field: mild for genuinely bad worlds (`missing`/`garbled`
  ≈ 1), but wasteful (5) when the value was actually `correct`.

### 5.5 Why asymmetry changes everything

Because ACCEPT costs 20 on any flaw but REPAIR/REJECT/FLAG are far cheaper, the
agent must **not** simply "pick the most likely world." Even if `correct` is the
single largest posterior, a modest chance of a flawed world can make ACCEPT the
*higher-cost* choice. Cost bends the decision away from raw probability — the job
of the expected-loss policy in §6.

*Concept receipts for this section live in `WORKING-CONTEXT.md` §6 (glossary).*

## 6. Policy: expected loss, thresholds, and buying information

This is the decision. The belief board (§4) and the cost matrix (§5) combine into
an action by **smallest expected loss** (Chapter 5), with derived thresholds, a
value-of-information rule for buying, and a human escape hatch.

### 6.1 The decision rule — smallest expected loss

For each action, its **expected loss** is the token-weighted average cost:

> `E[loss | action] = Σ_worlds P(world) × cost(action, world)`

**Rule: take the action with the smallest expected loss.** This is why the agent
must not "pick the most likely world" (§5.5): a low-probability world with a huge
cost can still dominate the average.

**Worked on the §4 posterior** (typo 0.402, unit_error 0.357, wrong_product 0.134,
correct 0.089, missing 0.009, garbled 0.009) against the §5 matrix:

| Action | Expected loss | |
|--------|:---:|---|
| ACCEPT | ≈ 0.089×0 + 0.911×20 ≈ **18.2** | 91% chance of publishing a lie |
| REPAIR | ≈ 0.089×18 + 0.357×0 + 0.134×8 + 0.402×4 + 0.018×12 ≈ **4.5** | |
| REJECT | ≈ 0.089×5 + 0.357×6 + 0.134×6 + 0.402×2 + 0.018×1 ≈ **4.0** | |
| FLAG | **2.0** | flat |
| **BUY** | **1.0** | flat — **smallest → chosen** |

The engine's answer: **don't guess — BUY more evidence.** A non-obvious, defensible
decision produced by the model, not by hand.

### 6.2 Thresholds (derived from the cost ratios, not guessed)

Rules of thumb fall out of §5's costs. ACCEPT (cost 20 if wrong, 0 if right)
beats FLAG (flat 2) only when:

> `(1 − P(correct)) × 20 < 2`  →  `1 − P(correct) < 0.10`  →  **`P(correct) > 90%`**

So **90% is the derived floor** where ACCEPT overtakes FLAG. We adopt a more
conservative **operating threshold of 95%** for ACCEPT — a safety margin for
publishing specs, since a residual 1–5% still carries the 20-unit downside.
Below threshold, we fall back to the loss-minimizing action (often BUY, then FLAG).

*(This "act only above a cost-derived confidence, else abstain to a human" rule is
textbook **reject-option / Chow's rule** classification — the AI probability review
confirmed it is the correct standard tool and worth naming, Sec 11.)*

**Calibration caveat (honesty; from AI reviews, Sec 11 — practitioner + preprint).**
This 95% threshold is only as trustworthy as the posterior is *calibrated*. In the
Step-11 run the top confidence bin (P(correct) ≥ 0.95) was only ~60% empirically
correct on 40 cases — i.e. the threshold does **not yet** correspond to a validated
real-world risk level and must **not** be read as "95% safe" operationally.

**If real, this is not cosmetic — it would break the expected-loss math (preprint +
probability reviews, Sec 11).** The whole §6.1 derivation of the ACCEPT threshold
assumes the posterior's `P(correct)` *is* the true probability of `correct`. If the
≥0.95 bin were really only ~60% correct, then the *true* expected loss of ACCEPT there
is ≈ 0.40 × 20 = **8**, far above FLAG (2) and even REJECT (5). In that case the policy
that says "ACCEPT at P ≥ 0.95" would in reality be choosing the **worse** action — the
miscalibration would *invert* the decision the expected-loss rule was supposed to make.
The math is only sound *once the posterior is calibrated*.

**Statistical honesty cuts both ways, though (AI probability review, Sec 11).** The
"~60%" is **3 of 5 cases** — the ≥0.95 bin has n = 5. A 95% Wilson interval on 3/5
runs roughly **0.23–0.88**, which cannot rule out either a serious problem *or* that
the bin is actually fine. So the correct statement is a **warning sign of
over-confidence whose magnitude N = 5 cannot establish** — not "the model is 60%
calibrated." We flag the *direction* (and its potential to invert the decision) but do
**not** assert the magnitude.

Either way the threshold is a *design target*, not an operating risk level. Making it
operational requires a calibrated posterior on an independently audited sample (see §8
open questions) — after which the ACCEPT threshold must be re-derived from the
*calibrated* probabilities, not the raw ones. The most likely *mechanistic* cause of
any over-concentration is the unstated conditional-independence assumption in chaining
(§4.6). Treat current numbers as a prototype, not a production guarantee.

### 6.3 Buying information — a budget heuristic (not true VOI)

**Honest naming (AI probability review, Sec 11):** what follows is a *value-of-
information-flavoured* rule, but rules 1–2 below are really a **budget heuristic**,
**not** true VOI. True VOI compares `E[loss now]` against `E[loss after the evidence]`
and buys only when the *expected reduction in loss* exceeds the fetch cost — it
requires predicting how the evidence would move the board. Our cost-cap ("never spend
more than FLAG = 2") sidesteps that prediction. It is a *defensible* Week-1
simplification, but calling it VOI overstates the rigor, so we label it a heuristic.
It can both over-buy (buy when no signal could move us across a threshold — the
VOI-zero pre-filter only catches the extreme case, not the marginal one) and under-buy
(stop at 2 when a cheap 3rd decisive probe exists). The fully-correct version is a
sequential decision / optimal-stopping problem (SPRT-flavoured), scoped out for Week 1.

**The heuristic — buy only if it *could* change the action, and never spend more than
the guaranteed FLAG resolution.** Two layered rules:

1. **VOI-zero pre-filter (cheap check, before any buy):** if buying cannot change
   the action, **do not buy.** Cases: `missing`/`garbled` dominate (no sound value
   to resolve), or every plausible remaining world already leads to the *same*
   action. Value = 0 → skip the fetch.
2. **Cost-cap stop rule (the workhorse):** FLAG costs 2 and guarantees a
   resolution, so **never spend more than 2 on buying.** With BUY = 1, that is a
   **hard cap of 2 buys**, then FLAG. This needs no prediction of future evidence
   — just a counter — and directly encodes that *cost* is what we optimize. (FLAG's
   cost is the natural ceiling on evidence-gathering spend.)

### 6.4 Stop / escalate rule (Act / Buy / Flag)

Per decision, in order:

1. **VOI-zero?** → skip buying; take the lowest-loss terminal action now.
2. **Threshold met** (`P(correct) ≥ 95%`, or one action's expected loss is clearly
   lowest)? → **act** (ACCEPT / REPAIR / REJECT) immediately; don't spend budget.
3. Else **BUY** (update the board via §4), while buy-count < 2.
4. **Buy budget exhausted (2 buys) or still uncertain** → **FLAG-FOR-HUMAN**,
   especially when the residual doubt hinges on human-only evidence (§2.3: image,
   page context, does-this-product-exist).

Note: a confident `correct` (≥95%) means **ACCEPT**, not FLAG — flagging is for
*unresolved* doubt, not for confidence.

### 6.5 What we achieved

The agent converts *belief + cost* into *action*, with a principled "get more
evidence first" that is bounded by the cheapest guaranteed resolution (FLAG), and
a human escape hatch for exactly the cases a machine cannot resolve. This policy
is what §7 exercises across many test cases.

*Concept receipts for this section live in `WORKING-CONTEXT.md` §6 (glossary).*

## 7. Experiment / test-case table

The engine's "unit tests." Each case is decided using **only the observations**
(source + value + evidence reading); the **true world is hidden at decision time**
and revealed afterward to score correctness + cost (no marking our own paper, §2).
Actions follow the §6 policy; costs follow the §5 matrix. We report **cost**, not
just accuracy (Chapter 0 lens).

Legend — Source: `MFR` manufacturer / `MID` mid-reliability / `SKY` sketchy.
Evidence: `IS` in-support, `OOS` out-of-support, `X✓` cross-source agrees, `X✗`
cross-source disagrees, `UNIT` plausible after unit conversion, `∅` empty, `JUNK`
unparseable. Correct? = did the action suit the (revealed) true world.

| # | Field | Scraped value | Src | Evidence | True world *(hidden)* | Action | Why this action | Correct? | Cost |
|---|-------|---------------|-----|----------|-----------------------|--------|-----------------|:---:|:---:|
| 1 | ram_gb | `8 GB` | MFR | IS, X✓ | correct | ACCEPT | MFR prior + in-support + agreement → P(correct) ≥ 95% | ✓ | 0 |
| 2 | ram_gb | `160 GB` | MID | OOS | typo | BUY→FLAG | §4 case: posterior spread, BUY first; if still unresolved after cap → FLAG | ✓ | 1–2 |
| 3 | storage_gb | `16000 MB` | MID | UNIT (→16 GB) | unit_error | REPAIR | converts cleanly to in-support 16 GB; REPAIR cost 0 in unit_error | ✓ | 0 |
| 4 | ram_gb | `8 GB` | SKY | IS | correct | BUY | sketchy prior keeps P(correct) < 95%; cheap BUY beats risky ACCEPT | ✓ | 1 |
| 5 | ram_gb | `6 GB` | MFR | IS, but X✗ (others say 8) | wrong_product | BUY→FLAG | in-support yet sources disagree → likely wrong variant; buy, else human | ✓ | 1–2 |
| 6 | weight_g | `1660 g` | MID | OOS (phone ~166 g) | typo | REPAIR/REJECT | 10× off → typo; drop or fix the extra digit | ✓ | ~2 |
| 7 | battery_mah | `` (empty) | MID | ∅ | missing | REJECT | VOI-zero (nothing to resolve) → drop the field, no buy | ✓ | 1 |
| 8 | ram_gb | `8&nbsp;GB` | MID | JUNK | garbled | REJECT/FLAG | unparseable; VOI-zero for buying; drop or hand off | ✓ | 1–2 |
| 9 | storage_gb | `256 GB` | MFR | IS, X✓ | correct | ACCEPT | high-trust source + agreement → confident publish | ✓ | 0 |
| 10 | ram_gb | `12 GB` | SKY | IS, X✓ | correct | BUY→ACCEPT | sketchy but agreement pulls P(correct) over threshold after 1 buy | ✓ | 1 |
| 11 | screen_in | `6.1 in` | MFR | IS, but true spec 6.7 | wrong_product | ACCEPT | *failure seed:* looks perfectly normal, MFR-trusted → wrongly accepted | ✗ | 20 |
| 12 | ram_gb | `4 GB` | MFR | IS, X✓ (all wrong) | wrong_product | ACCEPT | *failure seed:* every source copied the same wrong variant | ✗ | 20 |
| 13 | storage_gb | `0.5 TB` | MID | UNIT (→512 GB) | unit_error | REPAIR | TB→GB conversion lands in-support; repair | ✓ | 0 |
| 14 | battery_mah | `45000 mAh` | SKY | OOS | typo | BUY→FLAG | wildly high + sketchy; buy then escalate rather than guess | ✓ | 1–2 |

**Coverage:** all six worlds appear; all three sources; in/out-of-support,
cross-source agree/disagree, unit-convertible, empty, and junk evidence; and the
key policy behaviours (confident ACCEPT, cheap BUY, REPAIR, REJECT, BUY→FLAG
escalation). Rows **11–12 are deliberate failure seeds** for §8.

**Scaling note:** this batch (14 rows) is the starter set; §8 dissects the
failures, and the optional code (Step 11) can scale this toward 30–50 auto-scored
rows with confusion-matrix / cost metrics.

**Code results (Step 11, `src/` + `results/`).** The model was transcribed into a
runnable agent and scored over 40 labeled cases (labels hidden at decision time)
against two comparators: an **autonomous** policy (no human/no buy) and a **dumb
score+threshold baseline** (suggested by the r/learnmachinelearning discussion).
Findings (**preliminary, N = 40, no confidence intervals — do not over-read**): on
this sample the full policy has the lowest average decision cost (**2.30 vs ~3.10**)
and agrees with the baseline on only **62.5%** of cases, so the belief layer *changes*
decisions. **It does not yet follow that it "earns its keep" (preprint review, Sec 11).**
Two honest reasons the conclusion is over-stated as written:
- **The lower cost is largely bought by escalation, not by better calls.** The full
  policy routes **57.5%** of cases to a human vs. the baseline's ~32.5%; a fair
  comparison must hold the **human-review budget fixed** (or show fewer worst-case
  errors), which we have not done. In fact **all three deciders still miss the same
  two `wrong_product` seeds** (F1/F2, cost 20 each) — the belief layer does not reduce
  the catastrophic errors, it mostly moves the medium cases to the human queue.
- **The baseline's mechanics must be stated** for the comparison to mean anything: it
  is a single confidence score `P(correct)` with two fixed thresholds — ACCEPT if
  ≥ 0.90, REJECT if ≤ 0.40, else FLAG; **no per-world beliefs, no REPAIR, no BUY.**
  (Full definition in `src/agent.py::decide_baseline` and `results/README.md`.)

Also honest: the top confidence bin is not "slightly" off — it is **~60% empirically
correct** where the model claims ≥95%, a severe miscalibration that breaks the ACCEPT
math (§6.2). And the **cross-source correlation discount (policy 1.1)** is documented
in the audit record but is **not exercised by these 40 cases**, so it is a design
change, not yet an empirically demonstrated effect. See `results/README.md`.
**Significance test (added after the AI probability review, Sec 11).** The review
asked for a paired test rather than eyeballing a 0.8-unit gap on N=40, and *predicted
it wouldn't be significant.* We ran a **paired Wilcoxon signed-rank** on per-case cost
differences (`src/evaluate.py::paired_wilcoxon`). Result, honestly: the gap **is**
statistically significant (full vs baseline `p ≈ 0.015`; full vs autonomous
`p ≈ 0.003`) — but the **median per-case difference is 0.0**. That combination is the
real story: **most cases tie**, and the significant mean gap is driven by a *minority*
of cases where the full policy lands a cheaper action, not by a broad per-case
improvement. Read alongside the identical **2/2/2** catastrophes and the higher
escalation, the honest reading is: *the belief layer's lower cost is real (not pure
noise) but narrow — it comes from a few better mid-cases plus heavy escalation, not
from preventing the expensive wrong-publishes.* (Caveat still stands: normal
approximation, N=40 — indicative, and the test can't undo the active-learning eval
bias, §8.2 open-Q7.)

**Honest summary sentence:** *on a preliminary 40-case sample the full policy showed a
lower average decision cost (2.30 vs 3.10, paired Wilcoxon p≈0.015 but median per-case
diff = 0) primarily by routing 57.5% of cases to human review; it prevents no more
catastrophic wrong-publishes than the baseline (2/2/2), so a larger dataset and a
fixed-escalation-budget comparison are still needed to show it makes genuinely better
decisions rather than just escalating more.*

*Concept receipts for this section live in `WORKING-CONTEXT.md` §6 (glossary).*

## 8. Failure analysis and open questions

A model's honesty is measured by how clearly it states where it breaks (Chapter 0
cost lens: name the failure, name who pays). Below are the failure modes we know
about, ranked, followed by the honest "what it can't do" list.

### 8.1 Failure modes (world → action → cost → who pays)

**F1 — `wrong_product` blind spot *(highest severity)*.** A value that is
in-support *and* agrees with sources but is simply the wrong variant/revision
(table rows 11–12). world = `wrong_product` → action **ACCEPT** → **cost 20** →
paid by the **retailer** (reputation/returns) and the customer. The engine
*cannot* catch this from value + support + agreement alone; only manufacturer
proxy or human evidence resolves it. This is the failure that most directly
publishes a wrong value.

**F2 — Coordinated cross-source error.** All sources copied the same wrong value,
so cross-source agreement (which we treat as strong evidence for `correct`)
*falsely* boosts `correct`. world = `wrong_product`/`typo` → **ACCEPT** →
**cost 20**. Agreement is not independence; shared upstream errors defeat us.
*Design change from a discussion (Sec 5–7):* a practitioner on r/WebScrapingInsider
confirmed this ("5 sites showing the same value isn't useful if they're copying the
same feed; I trust consistency with the rest of the product more"). In response we
**down-weight correlated cross-source agreement** (treat agreeing copies as ~one
weak source) — `policy_version` 1.0 → 1.1. The effect is worked end-to-end in
`decisions/probability-decision-record.md`, where the discount flips a decision from
REPAIR to FLAG-FOR-HUMAN. Prefer *internal consistency* (value vs. the product's
other specs) as the harder-to-fake signal.

**F3 — Schema / key-mismatch *(highest frequency; boundary failure)*.** Sources
name/structure specs differently (e.g. "camera" under different keys), so the
crucial field is misidentified or missed *before* our per-field agent runs. This
lives at the **system boundary** we declared out of scope in §1 (upstream
routing). Effect: many crucial keys silently missing. Costly *in aggregate*
precisely because it is frequent; the agent never gets a chance to help. Recorded
as the most-forgotten failure.

**F4 — Mislabeled source reliability.** A sketchy source tagged as `mid`/`mfr`
selects an over-optimistic prior (§3.1) → `P(correct)` starts too high → premature
**ACCEPT** of flawed data → up to **cost 20**. Our whole prior hinges on a source
label we may get wrong.

**F5 — Stale support range.** A genuinely new/unusual-but-real product (e.g.
24 GB phone RAM when our range said max ~16) reads out-of-support → good value
wrongly **REPAIRed/REJECTed** → **cost ~5–18** (damages good data). Support ranges
decay as technology moves.

Severity ranking: **F1 > F2 ≈ F4 > F5**, with **F3 highest by frequency** (and
large in aggregate). The expensive failures all share one shape: they end in
publishing (or corrupting) a value the agent was too confident about.

### 8.2 Open questions / what it can't do (honest tab)

1. **Cannot verify images.** Listings reuse scraped product images; the agent has
   no way to check an image is the right product (pure human-only evidence, §2.3).
2. **Priors are assumed, not counted.** §3 boards are reasoned assumptions from
   B2C experience, not a labelled dataset — the base rate could be off.
3. **Cannot detect coordinated cross-source errors (F2).** Our agreement signal
   assumes source independence, which shared errors violate.
4. **Support ranges need ongoing maintenance (F5).** They must be updated as new
   hardware appears, or good values get flagged.
5. **Assumes correct upstream field identification (F3).** If the field was
   mislabeled/missed before the agent, it cannot recover it.
6. **No general way to justify the *strength* of a prior.** (Raised in the
   r/AskStatistics discussion.) We use weakly-informative priors (§3.2), but proving a
   strong prior is *right* has no general answer — a known Bayesian objection. Partial
   mitigations: plot prior vs. likelihood vs. posterior to see which dominates; calibrate
   against audited outcomes.
7. **Evaluation is biased by active learning.** (Raised by a practitioner in the
   r/learnmachinelearning discussion.) Because the agent auto-accepts a large bucket it
   never verifies and only humans see the flagged bucket, scoring only reviewed cases
   over-weights the hard ones. Honest fix (future work): randomly audit a slice of the
   auto-accepted bucket and **importance-weight** it back to estimate true
   population accuracy/calibration. The current `results/` numbers should be read with
   this caveat.
8. **FLAG assumes an infallible, flat-cost human.** (Raised by the preprint review,
   Sec 11.) The cost matrix treats FLAG as a flat **2** that *perfectly* resolves the
   case. Real reviewers have an error rate, a latency, and a per-item cost that grows
   with volume — so FLAG neither guarantees a correct resolution nor stays cheap at a
   57% review rate. A truer model gives FLAG a *distribution* over outcomes (some human
   errors) and a review-capacity constraint; this would raise the real cost of the
   full policy's heavy escalation and is the honest counterweight to the "earns its
   keep" claim (§7).
9. **Bayesian outputs inherit the assumptions' uncertainty.** (Raised by the preprint
   review, Sec 11 — "veneer of certainty".) The priors, likelihoods, and costs are
   labelled assumptions (§3, §4, §5), but feeding them through Bayes and expected-loss
   produces crisp-looking numbers ("90% is the derived floor", "P(correct) = 0.978").
   Those outputs are **conditional on the inputs**: they are internally consistent given
   the assumed numbers, not empirical facts. Every derived threshold and posterior in
   this document should be read as "*given* these stated assumptions", and would move if
   the assumptions were re-estimated from labelled data.

### 8.3 What would most improve the model next

Independent, high-trust evidence that breaks the F1/F2 blind spots: a manufacturer
proxy treated as *near*-ground-truth (still Layer 2, §2.2), and a source-
independence check so agreement across *correlated* sources counts for less. Both
target the expensive, confidently-wrong failures.

**Roadmap from the AI practitioner review (Sec 11) — accepted as future work.** These
are correct and important, but out of scope for a Week-1 thinking-first prototype (the
reviewer agreed "the decision-theoretic layer isn't the main production risk"); they
are recorded here as the path to production, not a Week-1 rebuild:
1. **Identity/variant resolution as a first-class subsystem** — resolve
   product → variant → region → revision → time *before* the field belief engine has
   authority. This is the real fix for the F1 `wrong_product` blind spot (currently
   scoped out at the §1 boundary).
2. **Model correlated evidence properly (principled, not a hand discount)** — the AI
   probability review (Sec 11) gave two concrete upgrades to the scalar policy-1.1
   discount, cheapest first:
   (a) **Effective sample size** — if `k` sources have pairwise copy-correlation `ρ`,
   the effective independent count is ≈ `k / (1 + (k−1)ρ)`; update on `n_eff`, not `k`.
   One parameter, defensible, and `ρ` is *estimable* from how often sources agree on
   values already known to be wrong. This is the cheap interim fix I'd implement first.
   (b) **Latent "shared upstream feed" node** — model a hidden syndicated-feed variable
   that copying sources read from; sources are conditionally independent *given the
   feed*, not marginally. This is the correct causal structure for F2 and the long-term
   answer (a manufacturer→distributor→retailer→comparison-site chain can make 5
   "sources" ≈ 1 observation). Same fix as the §4.6 chaining independence problem —
   solve it once with a joint/latent-cause model and both are handled.
3. **Loss-aware BUY / VOI** — the flat BUY cost undervalues *bad* evidence (a buy that
   returns the same wrong variant carries downstream risk, not just fetch cost). Note:
   the hard 2-buy cap is a *deliberate* Week-1 simplification (FLAG=2 is the natural
   ceiling), defensible but crude; a scalable version picks the next probe by expected
   publish-risk reduction per unit cost.
4. **Temporal / version / region semantics** — model each value as valid over a time
   interval for a specific entity, so temporally-stale-but-agreeing sources don't fool
   the agreement signal (extends F5 beyond the flat support range).
5. **Independently-audited gold set incl. auto-accepts** — same point as §8 open
   question 7; the ≥0.95 bin should be shown to hit high precision on an *independent*
   audit before the threshold is used operationally.
6. **Operational routing** — risk-tier fields (only high-impact fields get the full
   engine), and batch human review *per product* not per field (resolve identity once,
   validate the spec cluster together) to attack both the 57% review rate and F1.
7. **Cold-start** — a brand-new category with no support range wrongly flags genuinely
   novel values; hierarchical/time-aware support ranges (global→category→brand→family→
   cohort) mitigate this (extends F5).

*Concept receipts for this section live in `WORKING-CONTEXT.md` §6 (glossary).*

---

## 9. Measuring doubt in bits — entropy before/after (Week-2)

Week 1 tracked *which world leads*. That misses a second question the belief engine
should answer: **how confused is the agent overall, and did the evidence actually
reduce that confusion?** The one-number answer is **entropy** (Shannon), measured in
**bits**. Zero bits = certain; higher = belief spread across more worlds. One bit is
"one good yes/no question's worth of doubt". For `n` equally-likely worlds entropy is
`log2(n)`; here 6 equal worlds would be `log2 6 = 2.585` bits — that is the ceiling.

`H(belief) = − Σ_world P(world) · log2 P(world)`

### 9.1 The locked case: 160 GB RAM, out-of-support clue

We reuse the §4 numbers exactly (prior = the "mid"-reliability board from §3; the
single clue is *out-of-support*, `P(oos|world)` from §4.2). No new assumptions.

| Belief | correct | wrong_prod | unit_err | typo | missing | garbled | **Entropy** |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Prior** | 0.50 | 0.15 | 0.10 | 0.05 | 0.10 | 0.10 | **2.123 bits** |
| **Posterior** (after oos) | 0.089 | 0.134 | 0.357 | 0.402 | 0.009 | 0.009 | **1.880 bits** |

**Observed information gain = 2.123 − 1.880 = 0.243 bits.**

### 9.2 The uncomfortable, honest reading

The clue is *decision-relevant* — it flips the leader from `correct` (0.50) to `typo`
(0.402) and surfaces `unit_error` (0.357). Yet **entropy barely moved** (2.12 → 1.88,
only 0.24 bits). Why? The prior was already very unsure (2.12 of a possible 2.585
bits), and the clue mostly *redistributed* mass among three error worlds rather than
concentrating it on one. So:

> **Changing the top-ranked world is not the same as reducing doubt.** A clue can be
> highly *action-relevant* and still leave the agent almost as uncertain (in bits) as
> before. Accuracy of the top pick and entropy are different axes.

This is exactly why a single out-of-support flag is (correctly) *not* enough to ACCEPT
or REJECT — post-clue the agent still holds ~1.88 bits of doubt across typo /
unit_error / wrong_product, which is why the §6 policy routes this case to BUY/FLAG,
not a terminal action. The bits make the Week-1 "still uncertain, escalate" instinct
*quantitative*.

### 9.3 Expected vs. observed gain (the distinction that ranks clues correctly)

The 0.243 bits above is the gain *after seeing* `oos = true`. But **before** running
the check the agent doesn't know the outcome. The out-of-support check comes back:

- **oos = true** with prob `P(oos) = Σ prior·P(oos|world) = 0.112`; then `H = 1.880`.
- **oos = false** with prob `0.888`; then `H = 1.897` (gain 0.226 bits).

The honest value of *running* the check is the outcome-weighted average — the
**conditional entropy** `H(W | clue) = 0.112·1.880 + 0.888·1.897 = 1.895 bits`, so:

> **Expected information gain = H(prior) − H(W|clue) = 2.123 − 1.895 = 0.228 bits.**

Observed (0.243) ≈ expected (0.228) here only because the two outcomes leave similar
entropy; in general they differ, and **ranking clues by the observed number is a
classic error** (the brief flags it). §10 uses the *expected* number to choose which
clue to buy next.

*Arithmetic reproduced by a stdlib-only script; every number traces to §3/§4.
Concept receipts (entropy, information gain, conditional entropy) live in
`WORKING-CONTEXT.md` §6.*

---

## 10. Which clue to buy next — expected bits per unit cost (Week-2)

At decision time the agent already has the free clues and, on the 160 GB case, has
seen `out-of-support`. It now sits at the **post-oos posterior** (§4.3), whose entropy
is **1.881 bits**. The Week-2 question: of the three *costed* clues (§2.1 Tier B),
which is worth buying **next**? We rank by **expected information gain ÷ cost**
(bits per unit cost), using *expected* gain (§9.3), not the after-the-fact number.

### 10.1 The candidate clues and their likelihood models (assumptions, labelled)

Each clue is a two-outcome test; the table is `P(clue returns the "16 GB"-consistent
outcome | world)`. Costs are on the Week-1 scale (BUY = 1; manufacturer = 2 because it
is a fetch **+** parse of an official page). These are **author-set** assumptions with
reasoning (each number reasoned world-by-world, independent of the actual `160` value),
not measured — provenance recorded per row.

**Modelling note (author, Option A).** A `typo` does not imply the truth is 16 GB —
the intended value could be 1.6 / 15 / 16 / 1600 / … (a *nested* uncertainty inside the
typo world; the six worlds remain MECE as generating processes). Rather than model that
sub-distribution explicitly, we fold it into a **lower typo likelihood**: the maker
confirms *our* proposed 16 only *sometimes* under typo. Explicit intended-value
modelling is logged as future work (§8).

| Clue (cost) | corr | wrong_prod | unit_err | typo | miss | garb | Reasoning for the split |
|-------------|:--:|:--:|:--:|:--:|:--:|:--:|-------------------------|
| **Manufacturer proxy = "16 GB"** (2) | .90 | .15 | .82 | .35 | .05 | .05 | **Author-set (revised).** `correct` 0.90: real spec *is* 16, maker states it minus ~5–10% listing error. `unit_error` **0.82 (lowered from 0.90 on reflection)**: the truth is still 16 GB, but the maker lists clean *GB*, so a raw `16000 MB`-style unit_error is a touch less likely to surface as a literal "16 GB" match than an already-correct value — so it sits just below `correct`. `typo` 0.35 (Option-A: many intended values). `wrong_product` 0.15: usually a different variant, kept off the floor for *adjacent 16 GB sibling variants* the maker may list. `missing`/`garbled` 0.05 floor. |
| **Reference-dataset SKU match** (1) | .65 | .40 | .55 | .35 | .15 | .15 | **Author-set (revised).** The specific catalogue available here is itself **scraped, stale, and poorly maintained** — barely better than noise. So it gets the *flat* row: truth rows low (`correct` 0.65, `unit_error` 0.55) and error rows high (`wrong_product` **0.40**, `missing`/`garbled` 0.15). A near-flat row ⇒ tiny gap ⇒ tiny information (confirmed below). |
| **Cross-source agreement = "16 GB"** (1) | .75 | .20 | .65 | .28 | .10 | .10 | **Author-set (revised): a hand-picked panel of decent sites, not random retail.** With a better panel the copying confound is weaker, so this row is the *sharper* one: `correct` 0.75 / `unit_error` 0.65 well above `wrong_product` 0.20; `typo` 0.28 (Option-A). Wider gap ⇒ more discriminating. *(The generic broad-panel version would instead be flat/confounded; here the author's panel is specifically curated.)* |

### 10.2 Result — expected gain, and the reordering when cost enters

*Status: all three rows are now computed from the author's final numbers and
reproduced by committed code (`src/information.py`); the ranking/narrative below is
final.*

**Manufacturer proxy (author-set), worked live from the §4.3 belief:**

- Step 1 — predict the outcome: `P(positive) = 0.535` (near coin-flip → the agent
  genuinely doesn't know what the page will say).
- Step 2 — Bayes each way: **if positive**, belief → unit_error 0.548 / typo 0.263 /
  correct 0.150, wrong_product collapses to 0.038.
- Step 3 — average over both outcomes.
- **Expected info gain = 0.250 bits; bits-per-cost = 0.250 / 2 = 0.125.** *(Down from a
  0.317 first pass after the author lowered `unit_error` 0.90 → 0.82: a narrower
  correct-vs-unit_error gap ⇒ slightly less discrimination — the author's own
  "gap drives information" prediction, confirmed.)*

| Clue | Cost | **E[info gain]** | **Bits per cost** | Status |
|------|:--:|:--:|:--:|:--:|
| Manufacturer proxy | 2 | **0.250 bits** | 0.125 | author-set ✓ |
| Cross-source agreement | 1 | 0.135 bits | **0.135** | author-set ✓ |
| Reference-dataset match | 1 | 0.039 bits | 0.039 | author-set ✓ |

**Note — the bits-per-cost ranking now differs from the raw-bits ranking.** After the
revision the manufacturer still carries the most *raw* information (0.250 > 0.135) but
the cross-source panel wins **per unit cost** (0.135 > 0.125), because it delivers over
half the bits at half the price. This is the "highest-information clue is not the best
*buy*" tension appearing inside the author's own numbers (revisited in §12).

*Cross-source agreement (author-set, sharper row): P(pos)=0.440; H|pos=1.685,
H|neg=1.793 → H(W|clue)=1.746; expected gain = 1.881 − 1.746 = **0.135 bits**,
bits/cost 0.135. This is the author's curated-panel version (decent, near-independent
sites): still **less informative than the manufacturer** in raw bits (0.135 vs 0.250),
but after the manufacturer revision it now **wins on bits-per-cost** (0.135 vs 0.125).*

*Reference-dataset (author-set, flat row): P(pos)=0.451; H|pos=1.842, H|neg=1.841 →
expected gain = **0.039 bits**. Because the available catalogue is scraped/stale, its
row is nearly flat — whatever it returns, doubt stays ≈1.84 bits, so it is essentially
not worth buying.*

**Revision note (author).** The cross-source and reference likelihood rows were
**interchanged** after the author reconsidered the domain: the *specific* reference
catalogue on hand is scraped/stale (weak), while the cross-source *panel* is
hand-picked and near-independent (sharp). The copying-confound story still holds for a
*generic* broad panel; it just doesn't apply to this curated one. The computed bits are
the same two values (0.135, 0.039) attached to the swapped clues.

### 10.3 Final ranking and the redundancy test (author's merge hypothesis)

**Ranking (all author-set):** manufacturer wins on raw bits (0.250) but the cross-source
panel wins on **bits-per-cost** (0.135 vs 0.125) — the two rankings disagree; the
reference catalogue is a distant third and essentially not worth buying (0.039).

The author asked whether **cross-source agreement and the reference lookup are really
the same clue** and should be merged. We tested it instead of assuming it — measuring
the *weaker* clue's gain *after* the *stronger* one has already been bought (assuming
conditional independence given the world, the best case for it adding value):

- weaker clue **standalone** gain = 0.039 bits
- weaker clue gain **given the stronger already bought** = 0.033 bits
- → only **~16% redundant** with the stronger clue.

**The subtle finding (a genuine learning moment).** They are *not* redundant — but not
because the weaker clue adds real independent value. It keeps ~84% of its information
simply because **it barely had any information to begin with** (0.039 bits): a weak
clue cannot overlap much with anything. **Redundancy (do two clues measure the *same
thing*?) and strength (does a clue measure *anything*?) are different axes**, and this
case cleanly separates them. So the honest conclusion is *not* "merge them" — it is
"**don't buy the weak catalogue at all: it is too weak to matter**," which is a sharper
and more defensible statement than the merge would have been. (Logged as a new question
in §13: build a case where two clues are *strongly* informative *and* mutually
redundant, to show the agent must reason about joint — not summed — information.)

**Why the author's manufacturer row is sharper than the earlier scaffold (0.250 vs a
0.186 draft):** the author opened a *wider gap between the rows* — unit_error high
(0.82) while typo dropped to 0.35 (the Option-A intended-value insight) and
wrong_product to 0.15. A wider gap ⇒ more discrimination ⇒ more bits. *(The author
later lowered unit_error 0.90 → 0.82 on reflection, trading a little of that gap for a
more honest maker-lists-clean-GB assumption; bits fell 0.317 → 0.250 but the §11
decision was unchanged.)*

**Honest read (unchanged):** even the manufacturer's winning outcome only moves doubt
~1.88 → ~1.60 bits. No single affordable clue resolves this case (§9.2) — foreshadowing
§11, where *bits* and *decision value* come apart.

*Expected info gain here is identical to the **mutual information** between the clue
and the hidden world (§WC glossary) — the two names are the same quantity. Arithmetic
reproduced by a stdlib-only script from the §4.3 posterior. §11 turns "which next"
into "when to stop".*

---

## 11. When to stop buying — a true value-of-information rule (Week-2)

Week-1 §6.3 used a **flat 2-buy cap** and openly called it a *budget heuristic, not
VOI*. Week 2 replaces it with the real thing. **Bits are not the stop criterion —
rupees of expected loss are.** A clue is worth buying only if it is expected to
*change the action* enough to save more loss than it costs:

> **Value of information (VOI)** = `E[loss | best terminal action now]`
> − `E[loss | best terminal action after the clue]` (averaged over the clue's
> outcomes). **BUY iff VOI > cost(clue).** Otherwise **act/flag now.**

The second term must use the *expected* post-clue loss (§9.3): for each possible
outcome, re-choose the cheapest terminal action, then weight by how likely that
outcome is. Buying an *informative* clue that never changes the chosen action has
VOI = 0 — information without decision-relevance is worthless.

### 11.1 The 160 GB case: the best clue has zero decision value

At the post-oos posterior (§4.3) the terminal actions cost:

| Terminal action now | E[loss] |
|---------------------|:---:|
| **FLAG** | **2.00** ← best |
| REJECT | 4.21 |
| REPAIR | 4.50 |
| ACCEPT | 18.22 |

FLAG at a flat **2.00** already dominates. Now test **every** author-set clue from §10
— including the *most informative* one (manufacturer, 0.250 bits). For each, re-pick
the cheapest terminal action in both outcome branches:

| Clue (bits, cost) | if positive | if negative | E[loss after] | VOI | net VOI | decision |
|-------------------|:--:|:--:|:--:|:--:|:--:|:--:|
| Manufacturer (0.250, 2) | FLAG @ 2.00 | FLAG @ 2.00 | 2.00 | **0.00** | −2.00 | **don't buy** |
| Cross-source (0.135, 1) | FLAG @ 2.00 | FLAG @ 2.00 | 2.00 | **0.00** | −1.00 | **don't buy** |
| Reference (0.039, 1) | FLAG @ 2.00 | FLAG @ 2.00 | 2.00 | **0.00** | −1.00 | **don't buy** |

> **Every clue has VOI = 0 → DO NOT BUY. Flag now.**

In **all six** branches the cheapest action is still FLAG @ 2.00, so `E[loss after] =
2.00 = E[loss now]` for each clue. The reason (reasoned out by the author before
computing): even a *positive* manufacturer result only lifts `unit_error` to ≈0.55,
and REPAIR-ing on a ~0.55 belief eats the cost-18 penalty ~45% of the time — a worse
gamble than a guaranteed FLAG = 2.

**The headline result of the week:** the manufacturer clue is the *most informative*
option available (0.250 bits — it genuinely cuts doubt) yet is **worth 0 rupees to the
decision.** **Bits ≠ decision value.** This is also a different decision from Week-1,
whose flat 2-buy cap would have *spent* a buy (or two) before flagging; the VOI rule
catches that over-buy.

### 11.2 It is not "never buy" — VOI targets the boundary cases

VOI says buy precisely when a cheap clue can tip the *cheapest terminal action* across
a boundary. Sweeping `P(correct)` near the ACCEPT/FLAG frontier (confirming clue,
cost 1):

| `P(correct)` | Best terminal now | E[loss] after ref-lookup | Net VOI (−cost) | Decision |
|:---:|:---:|:---:|:---:|:---:|
| 0.40 (160 GB) | FLAG @ 2.00 | 2.00 | −1.00 | **flag now** |
| 0.86 | FLAG @ 2.00 | 0.88 | **+0.12** | **BUY** |
| 0.90 | ACCEPT @ 2.00 | 0.66 | **+0.34** | **BUY** |
| 0.92 | ACCEPT @ 1.60 | 0.55 | +0.05 | **BUY** |

So the rule is *selective*: it refuses to buy on hopeless, high-entropy cases (buy
can't beat FLAG's flat 2) **and** on already-decided cases, and spends only in the
narrow band where a confirmation flips ACCEPT below FLAG. The flat-cap heuristic
cannot make this distinction — it would buy the same fixed budget regardless.

### 11.3 The honest finding this exposes about our own cost matrix

FLAG's flat **2** is a *very strong ceiling*: because it guarantees resolution at a
low fixed price, VOI-positive buys exist only in a thin sliver near the ACCEPT
frontier. **Under this exact matrix, the belief engine should buy far less than
Week-1 assumed** — most doubtful cases should go straight to FLAG. That is either (a)
correct — human review really is cheap and buying is over-rated — or (b) a sign our
FLAG = 2 is *too optimistic* (it ignores human error, latency, and 57 %-review-rate
capacity cost; §8 open-question 8). Both readings are worth stating: **the VOI rule
turned a modelling assumption we had buried (flat FLAG cost) into a visible driver of
the whole buy policy.** The full sequential version (buy → re-evaluate VOI → buy
again) is an optimal-stopping / SPRT problem; the one-step VOI here is its greedy,
defensible first move.

### 11.4 The stop rule, restated (replaces §6.3's cap)

Per decision, act when **any** fires (whichever first):

1. **Belief is decisive** — one terminal action's E[loss] is clearly lowest (e.g.
   `P(correct) ≥` the cost-derived ACCEPT floor). Act.
2. **No affordable clue is VOI-positive** — `max_clue (VOI − cost) ≤ 0`. Act/flag now.
   *(This subsumes the old VOI-zero pre-filter and the cap.)*
3. **Evidence stopped moving belief** — two buys change the posterior by < ε (they are
   measuring the same correlated signal twice; §4.6). Act/flag.
4. Otherwise **BUY** the clue with the highest positive `VOI − cost` (§10 ranking),
   then re-evaluate.

*Arithmetic reproduced by a stdlib-only script from the §4.3 posterior and the §5.4
cost matrix. Concept receipts (value of information, optimal stopping) live in
`WORKING-CONTEXT.md` §6.*

---

## 12. Critical-thinking challenge (Week-2)

The brief asks us to break two comfortable intuitions using **our own numbers**.

### 12.1 "Always pick the highest-information clue." — False (two ways).

From the author's final §10 numbers, on the 160 GB case:

| Clue | E[info gain] | Cost | Bits/cost | VOI |
|------|:---:|:---:|:---:|:---:|
| Manufacturer proxy | **0.250 bits** (most) | 2 | 0.125 | 0 |
| Cross-source panel | 0.135 bits | 1 | **0.135** (best per rupee) | 0 |
| Reference catalogue | 0.039 bits | 1 | 0.039 | 0 |

The **most informative** clue (manufacturer, 0.250 bits) is **not** the one to buy, and
the numbers break the intuition *two independent ways*:

1. **Per unit cost, it loses.** The cross-source panel delivers 54 % of the bits at
   50 % of the price, so it wins on **bits-per-cost** (0.135 > 0.125). *Information is
   not free*; ranking by raw bits and ignoring price is a real, quantified mistake.
2. **For the actual decision, it is worth nothing.** The manufacturer clue's **VOI is
   0** (FLAG @ 2 dominates every branch, §11): buying the "best" clue would spend 2 and
   change no action. The most-informative option is decision-worthless here.

### 12.2 "Evidence always makes you more certain." — True *for our clues*, but not in general.

Entropy is an *expectation over outcomes*, so in principle a **single outcome can raise
it**. We checked all three author clues on the 160 GB case, and — honestly — **none of
them raises entropy in either branch**:

| Clue | H if positive | H if negative | start = 1.881 |
|------|:---:|:---:|:---:|
| Manufacturer | 1.588 (−0.29) | 1.680 (−0.20) | both fall |
| Cross-source | 1.685 (−0.20) | 1.793 (−0.09) | both fall |
| Reference | 1.842 (−0.04) | 1.841 (−0.04) | both fall |

So on *our* numbers this fallacy does **not** trigger, and we refuse to manufacture a
row just to make it. But it is a real phenomenon, and it is worth stating *when* it
happens: **a clue raises uncertainty on an outcome that contradicts the current
front-runner.** Here the front-runners (`typo` 0.40, `unit_error` 0.36) sit on
*out-of-support/error* worlds, and a "no, not 16" result is *consistent* with them, so
even the negative branch keeps concentrating rather than scattering. Had the belief
been strongly on `correct` and a clue came back "not 16", *that* would have scattered
mass and raised entropy. **The durable lesson survives either way:** judge a clue by
its **expected** effect before running it, never by hoping a particular result will
calm you down — which is exactly why the §11 stop rule averages over outcomes.

### 12.3 The unifying point

Both intuitions fail by collapsing a distribution to a point. Raw bits ignore cost;
"evidence reassures" ignores that gain is an average over outcomes (and can, in the
right belief state, be negative on a branch). The belief engine avoids both by always
working with the *full* outcome distribution and the *cost* of acting on it.

*Numbers reproduced by a stdlib-only script from the §4.3 posterior and the author's
final §10 likelihoods. Concept receipts live in `WORKING-CONTEXT.md` §6.*

---

## 13. Generalization and new questions (Week-2)

### 13.1 One environment change — make the human expensive (a *falsified* hypothesis)

The single most load-bearing assumption the information layer exposed (§11.3) is
**`FLAG = 2`, flat**. So we changed *only* that and tested a natural hypothesis.

> **Hypothesis (author):** VOI is 0 (§11) *because* FLAG @ 2 is a cheap, safe ceiling;
> therefore **raising the human cost should make buying worthwhile** — the "act now"
> fallback gets dearer, so a clue has more room to add value.
>
> **Environment change:** raise FLAG from 2 toward 5+ (busy reviewer / queue / some
> human error), everything else fixed.

**What actually happened (VOI of the author's clues vs. FLAG cost):**

| FLAG cost | Best "act now" | Manufacturer VOI (need > 2) | Cross-source VOI (need > 1) | Buy? |
|:--:|:--:|:--:|:--:|:--:|
| 2 | FLAG @ 2.00 | 0.00 | 0.00 | no |
| 4 | FLAG @ 4.00 | 0.21 | 0.14 | no |
| 5 | **REJECT @ 4.21** | 0.38 | 0.23 | no |
| 10 | REJECT @ 4.21 | 0.38 | 0.23 | no |
| 15 | REJECT @ 4.21 | 0.38 | 0.23 | no |

**The hypothesis is falsified.** VOI does rise off zero (the author's mechanism was
directionally right), but it **plateaus** at 0.38 / 0.23 and **never clears the clue
cost — at any human price.** The reason is subtle and worth stating: once FLAG ≥ 5 the
cheapest fallback stops being FLAG and becomes **REJECT @ 4.21**, which is *capped by
the cost matrix* and independent of FLAG. So raising the human cost merely switches the
*fallback* (FLAG → REJECT); it does **not** make the *clue* valuable.

> **The honest general lesson:** on a high-entropy case like 160 GB, buying is
> essentially never worth it — **not because the human is cheap, but because the belief
> is too foggy for any single clue to escape into a cheap terminal action.** To make
> buying pay you need a belief already *near a decision boundary* (§11.2's VOI-positive
> band by the ACCEPT frontier), or a much cheaper/sharper clue — not just a pricier
> human. The prediction-then-test *falsified* the tidy "expensive human revives buying"
> story, which is a stronger and more defensible result than confirming it.

*(Caveat retained: `FLAG = 2` flat-and-infallible is still an over-simplification —
real reviewers have latency, capacity, and error, §8 open-Q8. The point here is
narrower and now tested: fixing that assumption alone does **not** rescue buying on
foggy cases.)*

### 13.2 New questions raised by our own results

Not restatements of Week-1 open questions — these are questions the *information
analysis itself* produced:

1. **Why is expected info gain everywhere so small (≤ 0.25 bits)?** Every affordable
   clue barely dents 1.88 bits. Is the true bottleneck that our clues are mutually
   *redundant* (all keyed on "is 16 plausible?"), so their **joint** mutual information
   is far below the sum of individual gains? Measuring pairwise MI between clues would
   tell us whether buying two clues is worth ~1.1× or ~2× one clue.
2. **Where exactly is the VOI-positive band, as a function of the cost matrix?** We
   found it empirically near `P(correct) ∈ [0.86, 0.92]`. Can we derive the band's
   edges in closed form from (ACCEPT, FLAG, clue-cost, clue-likelihood)? That would
   turn "should I buy?" into a lookup, not a simulation.
3. **How far can the three rankings (raw bits, bits-per-cost, VOI) diverge?** Our own
   case already shows two of them splitting: the manufacturer wins raw bits (0.250) but
   the cross-source panel wins bits-per-cost (0.135 > 0.125). And VOI collapses the
   distinction entirely here (all three = 0). Construct a case where *all three*
   rankings pick *different* clues — e.g. one clue high-bits/low-VOI (shifts entropy but
   never crosses an action boundary) vs. one low-bits/high-VOI (small shift, but right
   at a boundary). That would prove decisively that the engine must rank by VOI, not
   bits or even bits-per-cost.
4. **How correlated are our clues with the *out-of-support* signal we already spent?**
   If the reference-lookup mostly re-measures "is this in a plausible range", its
   gain *conditional on* the oos clue is smaller than in isolation — the §4.6 chaining
   independence problem, now visible in the information budget.

*These feed the paper's "future work" and are logged in `WORKING-CONTEXT.md` §W2.*

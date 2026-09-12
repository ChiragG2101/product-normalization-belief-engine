# Review Record (Section 11) — AI reviews of the belief engine

This file holds (a) three ready-to-paste **review prompts** and (b) a **log** of the
real reviews you run and how you adjudicated each comment.

**Rules (course discipline):**
- **You run the reviews, not the assistant.** Paste each prompt below into a fresh
  ChatGPT / Gemini / Claude session (and attach the real files —
  `decisions/belief-engine-decision-model.md` and `results/report.md`), then paste
  the model's output back into the log. Nothing here is a fabricated review.
- **You adjudicate every comment:** record **accept / reject + a one-line reason.**
  Rejecting a reviewer with a good reason counts as much as accepting one — it shows
  judgment, not compliance.
- Any comment you **accept** should produce a real edit (to the model, code, or
  results) — note where it landed, exactly like the discussion "wired into" column.

**How to use:** run each prompt in its **own fresh chat** (no context bleed — one
chat = one review = one log section), ideally **spread across different models** so
you're not getting one model's blind spots three times. Suggested split: Practitioner
→ ChatGPT, Probability → Claude, Preprint → Gemini (swap freely). Attach the real
file(s) each time. That's **3 reviews total**, not nine.

---

## Shared summary block (paste this at the top of each prompt if you are NOT attaching files)

**Problem.** An agent decides, per scraped e-commerce product-spec field (e.g.
`ram_gb`, `storage_gb`, `weight_g`), whether the value is safe to publish when the
true canonical spec is unknown. Actions: ACCEPT / REPAIR / BUY-more-evidence /
FLAG-FOR-HUMAN / REJECT.

**Hidden states (MECE):** correct / unit_error (e.g. 16000 MB) / wrong_product
(right-looking value, wrong variant) / typo / missing / garbled.

**Belief.** Start from a source-reliability prior (manufacturer / mid-retail /
sketchy), split over the 6 states; update with Bayes on cheap evidence signals
(value out-of-plausible-range, unit-convertible, cross-source agreement/disagreement,
empty, junk). Priors are weakly-informative *assumptions* (not counted from labels).

**Cost (asymmetric).** Relative pain units: ACCEPT-a-flaw = 20 (worst),
bad-REPAIR-of-correct = 18, REJECT-correct = 5, FLAG = 2, BUY = 1. Publishing a
wrong value dominates.

**Policy.** Choose the action with the smallest expected loss. Derived ACCEPT
threshold P(correct) ≥ 95%. Buy more evidence only if value-of-information is
positive, hard-capped at 2 buys (FLAG costs 2), then FLAG.

**Cross-source caveat.** Agreement is down-weighted because sources copy each other
(not independent) — a design change from a practitioner discussion.

**Results (40 labeled cases, labels hidden at decision time; 3 deciders — full
belief policy, autonomous no-human/no-buy policy, dumb score+threshold baseline):**
full avg decision cost 2.30 < autonomous 3.08 ≈ baseline 3.10; full vs. baseline
agree on only 62.5% of cases (so the belief layer changes decisions); full policy
human-review rate 57%; all three miss 2 deliberate wrong_product failure seeds;
top confidence bin (P≥0.95) is only ~60% empirically correct — a **severe
miscalibration** (3/5 on N=40) that breaks the ACCEPT expected-loss math (true
E[ACCEPT]≈8 > FLAG 2). Known bias: evaluation is active-learning-biased (auto-accepted
bucket unverified); FLAG is modelled as a flat cost 2 that perfectly resolves (no human
error); results are preliminary (N=40, no confidence intervals).

---

## Prompt 1 — Practitioner review (e-commerce data pipeline)

You are a senior data engineer who has spent years building **e-commerce product
catalog** pipelines — scraping/ingesting specs from retailers and manufacturers,
deduping variants, and keeping published product data correct at scale. Review the
design below as if it were proposed for a real catalog pipeline you own.

Be adversarial and concrete. **Do not be complimentary; assume it has flaws.**
I want to find problems now, not in production.

[PASTE the shared summary block above, and/or attach
`decisions/belief-engine-decision-model.md` + `results/report.md`.]

Answer specifically:
1. The **3 weakest points** for a real e-commerce catalog at scale (millions of
   SKUs, many sources, specs that differ by region/variant/revision).
2. The **most likely way this fails in production** in the first month, and what
   signal would warn me.
3. Where does the **per-field, per-(category,field) support range** approach break
   (new categories, fast-moving specs, localized units like g vs oz)?
4. Is a **57% human-review rate** viable operationally? If not, what specifically
   would you change (thresholds, which fields get the full treatment, batching)?
5. What crucial failure mode am I missing? (I already know about: schema/key
   mismatch across sources, coordinated cross-source copying, stale support ranges,
   mislabeled source reliability, wrong-variant values that look normal.)
6. One thing that would **change your mind** and make you trust this in production.

End with a prioritized list: **[must-fix] / [should-fix] / [nice-to-have].**

---

## Prompt 2 — Probability / statistics review

You are a Bayesian statistician reviewing a small **discrete decision-theoretic
model**. Judge the *correctness* of the probability, not the prose. Be rigorous and
adversarial; **assume there are modeling errors and find them.**

[PASTE the shared summary block above, and/or attach
`decisions/belief-engine-decision-model.md`.]

Answer specifically:
1. Is the **prior → likelihood → posterior** update applied correctly, including
   when I **chain** multiple evidence signals (posterior of one becomes prior of the
   next)? Any independence assumption I'm smuggling in that's wrong?
2. My likelihoods `P(evidence | world)` are **independent per-world probabilities**
   (they don't sum to 1). Is that the right object, and am I using it correctly?
3. The cross-source-agreement signal is **correlated** (sources copy each other). I
   down-weight it by hand. Is there a **principled** way to model correlated evidence
   here instead of an ad-hoc discount?
4. Priors are **weakly-informative assumptions** with no labeled data. Is my claim
   ("evidence dominates once it's strong; the prior only carries weak-evidence
   cases") correct? How would you **calibrate** these priors cheaply?
5. Is **minimum expected loss** over actions (with an explicit FLAG/abstain option)
   the right decision rule? Am I missing a standard tool (e.g. reject-option
   classification, value-of-information formalism, sequential testing)?
6. My **calibration** shows the top confidence bin (P≥0.95) is only ~60% correct.
   What does that imply, and how should I fix over/under-confidence given my cost
   asymmetry?

End with: the **single biggest statistical mistake** (if any), and whether the
conclusions (belief layer beats baseline on cost) are **statistically supported**
by 40 cases or whether that's over-claiming.

---

## Prompt 3 — Preprint / scientific-writing review

You are a reviewer for a short technical preprint. Review the write-up below for
**honesty, clarity, and whether the claims are supported by the evidence** — not for
whether the idea is nice. Be adversarial; **flag every overclaim and unsupported
number.**

[PASTE the shared summary block above, and/or attach
`decisions/belief-engine-decision-model.md` + `results/report.md`.]

Answer specifically:
1. Which **claims are not supported** by the evidence presented (or are supported
   only by 40 hand/generated cases)? Quote them.
2. Is the **asymmetric cost matrix** presented as a *stated assumption* or smuggled
   in as fact? Same question for the priors and likelihoods.
3. Are the **limitations honest and complete**, or is anything important buried or
   missing? (I claim: active-learning eval bias, can't verify images, can't catch
   coordinated cross-source errors, priors unjustified in general, support ranges
   decay, assumes correct upstream field ID.)
4. Does the **"belief layer earns its keep" conclusion** follow from the results, or
   is it overstated? What would make it convincing?
5. What's **missing structurally** for a credible preprint (methods reproducibility,
   baseline description, threats to validity, related work)?
6. Rewrite my **single most overstated sentence** into an honest version.

End with a verdict: **[accept as honest draft] / [revise] / [major concerns]**, plus
the top 3 fixes before publishing.

---

## Review log  *(YOU fill this after running the prompts — not fabricated)*

For each review, record which model you used, then one row per notable comment with
your accept/reject decision and reason. Accepted comments should point to the edit.

### Review 1 — Practitioner (e-commerce)  ·  model: ChatGPT  ·  date: 2026-08-30
Overall verdict from the reviewer: *"A good decision-theory prototype but not yet a
production catalog-control system. The decision-theoretic layer isn't the main
production risk; the risk is giving a sophisticated decision layer insufficiently
reliable evidence about product identity and evidence independence."* Priority list:
6 must-fix, 6 should-fix, 5 nice-to-have. **Adjudication stance:** the reviewer is
high-quality and mostly right, but this is a **Week-1 thinking-first prototype** — so
most points are **accepted as future work / roadmap** (recorded in decision model
§8.3), with two cheap **honesty edits made now**. Nothing rejected outright; the one
point partially pushed back on is the 2-buy cap (a deliberate simplification).

| # | Reviewer comment (short) | Accept / Reject | Reason | Wired into (file/section) |
|---|--------------------------|:---:|--------|---------------------------|
| MF1 | Make product/variant/region/revision **identity** a first-class subsystem (value-level signals can't catch wrong-variant) | Accept → future work | Correct; it's the real fix for the F1 `wrong_product` blind spot, but it's an upstream subsystem scoped out at the §1 boundary — roadmap, not a Week-1 rebuild | Decision model §8.3 (roadmap #1); reinforces F1 |
| MF2 | **Fix calibration before using the 95% threshold operationally** (≥0.95 bin only 60% correct) | **Accept → acted now** | Sharpest + cheapest point; the threshold must not read as an operational risk level on 40 cases | Decision model §6.2 calibration caveat; `results/README.md` calibration note |
| MF3 | Replace scalar agreement discount with **evidence lineage / provenance graph** | Accept → future work | Right extension of the policy-1.1 correlation discount; too big for Week 1 | Decision model §8.3 (roadmap #2) |
| MF4 | BUY/VOI should use **downstream loss**, not flat cost + hardcoded 2-buy cap | Partial accept → future work + defend | Flat BUY cost undervaluing bad evidence is fair; but the 2-buy cap is a *deliberate* simplification (FLAG=2 is the natural ceiling) — kept, labelled crude | Decision model §8.3 (roadmap #3, with the defense noted) |
| MF5 | Build an **independently-audited gold set incl. auto-accepts** | Accept → future work | Same as the Reddit active-learning/eval-bias point — cross-validated; already a limitation | Decision model §8 open-Q7 + §8.3 (roadmap #5) |
| MF6 | Add **temporal / version / region semantics** to evidence | Accept → future work | Correct; extends stale/`wrong_product` handling beyond a flat support range | Decision model §8.3 (roadmap #4) |
| S1 | `unit_error` too narrow — real errors are **measurement-definition** (net vs gross weight, diagonal vs width, advertised vs usable) | **Accept → acted now** | Insightful and cheap; broadens the world's scope honestly | Decision model §1 `unit_error` note; §8.3 (roadmap) |
| S2 | **Cold-start**: new category → novel value → wrongly flagged/rejected | Accept → future work | Ties to F5; hierarchical/time-aware support ranges mitigate | Decision model §8.3 (roadmap #7); extends F5 |
| O1 | 57% review not viable at scale → **risk-tier fields + batch review per product** | Accept → future work | Excellent operational insight; reinforces the "57% is a tuning target" note | Decision model §8.3 (roadmap #6) |

### Review 2 — Probability / statistics  ·  model: Claude  ·  date: 2026-08-30
Single biggest statistical mistake flagged: **using the raw posterior `P(correct)` as
if calibrated when deriving/operating the ACCEPT threshold** — with the top bin at
~60% empirical the true `E[ACCEPT] ≈ 8 ≫ FLAG 2`, which *inverts* the loss-minimizing
decision. (Confirms the Gemini P1 finding; adds the mechanistic root cause below.)
**Adjudication stance:** the strongest, most rigorous review — it *validated* the core
Bayesian mechanics (single update, likelihood object, min-expected-loss + abstain) and
found two genuinely new technical issues (unstated conditional independence in
chaining; the 2-buy cap is a budget heuristic, not VOI) plus two honesty-sharpeners (a
Wilson interval on the "60%"; run a paired significance test). **Every point accepted;
nothing rejected**, with two self-corrections to my earlier edits.

| # | Reviewer comment (short) | Accept / Reject | Reason | Wired into (file/section) |
|---|--------------------------|:---:|--------|---------------------------|
| Q1 | **Chaining smuggles conditional independence** (`P(e₁,e₂\|w)=P(e₁\|w)P(e₂\|w)`); oos & xsource-disagree share a latent cause given typo → over-concentration = likely root cause of the top-bin over-confidence | **Accept → stated now + future work** | New, correct, and it explains the calibration gap mechanistically; cheap to state, real fix (joint likelihood / weight-of-evidence temperature) is future work | Decision model §4.6 (assumption stated); §6.2 (named as mechanistic cause); §8.3 roadmap #2 |
| Q2 | Likelihoods are the **right object** (per-world, needn't sum over worlds) — validated; **nit:** multi-valued signals must sum to 1 **over outcomes** or "absent" leaks mass | **Accept → note now** | Free credibility (a Bayesian validated the core) + an honest rigor nit worth enforcing in code | Decision model §4.2 (validation + sum-to-1 nit) |
| Q3 | Principled cheap alt to the hand discount: **effective sample size** `k/(1+(k−1)ρ)`; or a **latent shared-feed node**. Same fix as Q1 | **Accept → sharpen roadmap** | Upgrades the provenance-graph roadmap from "someday" to a one-parameter interim fix; `ρ` is estimable from agreement on known-wrong values | Decision model §8.3 roadmap #2 (a)+(b) |
| Q4 | "Evidence dominates" **overstated for a single signal** (the §4 worked case is a counterexample); calibrate priors cheaply via a **prior-predictive check** (no labels) | **Accept → correct §3.2 + add method** | My §3.2 wording over-claimed; the label-free `Σ prior×likelihood` vs observed-frequency check is genuinely cheap and stronger than "plot prior vs posterior" | Decision model §3.2 (two new bullets) |
| Q5 | The 2-buy cap is a **budget heuristic, not VOI**; name **Chow's rule** (reject-option) + optimal stopping | **Accept → relabel now** | I had been calling §6.3 "VOI"; honest relabel + citing the standard tools is cheap and correct | Decision model §6.2 (Chow's rule named); §6.3 (retitled "budget heuristic, not VOI") |
| Q6a | Miscalibration **inverts** the decision (E[ACCEPT]≈8) | **Accept → already done** | Confirms the Gemini P1 edit was right | Decision model §6.2 (from Review 3) |
| Q6b | **But "60%" is 3/5** (n=5); Wilson ≈ 0.23–0.88 → flag *direction*, don't quantify *magnitude* | **Accept → self-correction now** | I over-hardened "severe" in the Review-3 edit; walked it back to "warning sign, magnitude unquantifiable at N=5" | Decision model §6.2 (softened); `results/README.md` calibration |
| C1 | Cost win is **escalation, not better calls** (2/2/2 catastrophes; autonomous even has *higher* accept precision 0.818 vs 0.75) | **Accept → already reframed + add precision point** | Mostly done via Review 3; added the sharp "autonomous beats full on accept precision" observation | Decision model §7; `results/README.md` (table already shows it) |
| C2 | **Run a paired Wilcoxon** on per-case cost diffs; report a CI — don't assert a win on N=40 by eye | **Accept → implemented in code** | Cheap and we had the data; ran it. Honest result: gap **is** significant (p≈0.015) but **median diff = 0** (most cases tie) — real but narrow | `src/evaluate.py::paired_wilcoxon`; `results/report.md` + `results/README.md`; decision model §7 |

### Review 3 — Preprint / writing  ·  model: Gemini (two independent answers, A + B)  ·  date: 2026-08-30
Verdict [accept as honest draft / revise / major concerns]: **A = major concerns · B = revise.**
Both answers **independently converged** on the same core findings (calibration is
severe not slight; "earns its keep" is bought by escalation; baseline undefined; N=40
too small; FLAG assumed infallible) — that agreement across two runs makes the findings
hard to wave away, so they were treated as high-confidence. **Adjudication stance:**
every substantive point **accepted**; the sharpest (P1, calibration breaks the
expected-loss math) was acted on immediately, along with three other cheap honesty
edits (reframe "earns its keep", define the baseline, N=40/no-CI caveat). Structural
preprint gaps (methods, related work, threats-to-validity) routed to **Step 13** (the
preprint is where those sections get written). One **mild pushback** on P7. Nothing
rejected outright — the review was correct.

| # | Reviewer comment (short) | Accept / Reject | Reason | Wired into (file/section) |
|---|--------------------------|:---:|--------|---------------------------|
| P1 | "Slightly overconfident" understates it — ≥0.95 bin at ~60% correct **breaks the expected-loss math** (true E[ACCEPT] ≈ 0.4×20 = 8 > FLAG 2 > REJECT 5) | **Accept → acted now** | The most valuable catch in any review: it's a *correctness* bug, not cosmetics — the miscalibration inverts the ACCEPT decision the §6 rule was supposed to make | Decision model §6.2 (rewritten consequence) + §7 code-results; `results/README.md` calibration section |
| P2 | "Belief layer earns its keep" is overstated — lower cost is bought by routing 57.5% to humans; compare at a **fixed human-review rate** / show fewer worst-case errors | **Accept → acted now + future work** | Both answers raised it independently; the honest reframe is cheap, and the fixed-budget comparison is a real experiment | §7 code-results + `results/README.md` findings 1–3; future test noted |
| P3 | The **"dumb baseline" is never defined** (mechanics/thresholds) | **Accept → acted now** | Fair — the summary/preprint must be self-contained; baseline was only defined in code | §7 code-results now states ACCEPT≥0.90 / REJECT≤0.40 / else FLAG, no worlds/REPAIR/BUY; `results/README.md` already had it |
| P4 | **N=40 is too small** for the cost claim; no confidence intervals / variance | **Accept → acted now (caveat) + future work** | Correct; reworded to "preliminary, N=40, no CIs"; scale to N>500 + CIs is future work | §7 code-results + `results/README.md` headline preamble |
| P5 | **FLAG treated as flat cost 2 that perfectly resolves** — ignores human error rate/latency/capacity | **Accept → new limitation + future work** | Genuinely missing; it's the honest counterweight to "earns its keep" | Decision model §8.2 open-Q8; `results/README.md` finding 3 |
| P6 | Cross-source **correlation fix (policy 1.1) is referenced but not demonstrated** in the 40 cases | **Accept → noted honestly** | True — the flip lives in the audit record, not the metrics run; call it a design change, not a shown effect | §7 code-results caveat |
| P7 | Priors/costs "**smuggle authority** through Bayesian formulas — veneer of certainty on made-up numbers" | **Partial accept → note, mild pushback** | Fair *warning*, but provenance is already labelled everywhere (the course asked for exactly that); honest response is to state outputs inherit the inputs' uncertainty, not to over-concede | Decision model §8.2 open-Q9 (outputs are conditional on assumptions) |
| P8 | Structural gaps: **methods reproducibility, sampling description, related work, threats to validity** | **Accept → route to Step 13** | These are the preprint's job; the preprint step adds methods/baseline/related-work/threats sections | Deferred to Step 13 (preprint) — logged as build items |

---

## Changes made because of the AI reviews  *(fill as you accept comments)*
- **Review 1 / MF2 (calibration):** added a caveat that the 95% ACCEPT threshold is a
  design target, not a validated operational risk level (≥0.95 bin only 60% correct on
  40 cases). → decision model §6.2 + `results/README.md`.
- **Review 1 / S1 (measurement-definition errors):** noted `unit_error` is narrow and a
  broader class of semantic/measurement-definition errors exists. → decision model §1.
- **Review 1 / MF1,3,4,5,6 + S2 + O1:** accepted as **future-work roadmap** (identity
  subsystem, provenance graph, loss-aware VOI, temporal/region semantics, audited gold
  set, risk-tiering + per-product review, cold-start). → decision model §8.3.
- **Review 3 / P1 (calibration breaks the math):** rewrote the §6.2 caveat + `results/README.md`
  calibration section to state the *consequence* — true E[ACCEPT] ≈ 0.4×20 = 8 in the ≥0.95
  bin, so the miscalibration inverts the ACCEPT decision; threshold must be re-derived from a
  *calibrated* posterior. Also softened "slightly overconfident" → "severe miscalibration"
  everywhere. → decision model §6.2, §7; `results/README.md`.
- **Review 3 / P2, P3, P4, P6 (earns-its-keep / baseline / N=40 / correlation):** reframed the
  §7 code-results + `results/README.md` findings — cost win is preliminary (N=40, no CIs) and
  is largely bought by 57.5% escalation; added the honest one-sentence summary; defined the
  baseline inline (ACCEPT≥0.90 / REJECT≤0.40 / else FLAG); noted the policy-1.1 correlation
  discount is not exercised by the 40 cases. → decision model §7; `results/README.md`.
- **Review 3 / P5 (FLAG not infallible):** added open-Q8 — FLAG's flat cost 2 assumes a perfect,
  infinite-capacity human; a real reviewer has error/latency/cost that grows with volume. →
  decision model §8.2; `results/README.md` finding 3.
- **Review 3 / P7 (veneer of certainty):** added open-Q9 — every derived threshold/posterior is
  *conditional on* the stated assumptions, not an empirical fact. → decision model §8.2.
- **Review 3 / P8 (preprint structure):** methods/sampling/related-work/threats-to-validity
  routed to **Step 13** (the preprint step writes those sections).
- **Review 2 / Q1 (conditional independence in chaining):** stated the smuggled
  assumption openly, gave the fixes (joint likelihood / weight-of-evidence temperature),
  and named it as the likely mechanistic root cause of the top-bin over-confidence. →
  decision model §4.6, §6.2, §8.3 roadmap #2.
- **Review 2 / Q2 (likelihood object):** recorded the Bayesian's validation + the
  multi-valued-signal sum-to-1-over-outcomes rigor nit. → decision model §4.2.
- **Review 2 / Q3 (correlated evidence, principled):** upgraded roadmap #2 to the
  effective-sample-size formula `k/(1+(k−1)ρ)` + latent shared-feed node. → §8.3.
- **Review 2 / Q4 (priors):** corrected the "evidence dominates" over-claim (single
  strong signal still leaves the prior steering) and added the label-free
  prior-predictive calibration check. → decision model §3.2.
- **Review 2 / Q5 (VOI vs budget):** retitled §6.3 "a budget heuristic (not true VOI)",
  explained the difference, and named Chow's reject-option rule + optimal stopping. →
  decision model §6.2, §6.3.
- **Review 2 / Q6b (self-correction):** softened the Review-3 "severe miscalibration"
  to "warning sign; magnitude unquantifiable at N=5" with the Wilson interval. →
  decision model §6.2; `results/README.md`.
- **Review 2 / C2 (significance test) — new code:** implemented a pure-stdlib paired
  Wilcoxon signed-rank in `src/evaluate.py`; regenerated `results/`. Honest outcome:
  the cost gap IS significant (full-vs-baseline p≈0.015, full-vs-autonomous p≈0.003) but
  the MEDIAN per-case diff is 0.0 (most cases tie) — real but narrow, and it doesn't
  touch the 2/2/2 catastrophes. → `src/evaluate.py`, `results/report.md`,
  `results/README.md`, decision model §7.

## Comments deliberately rejected / pushed back on (with reason)  *(judgment, not compliance)*
- **Review 1 / MF4 (partial):** kept the **hard 2-buy cap** rather than replacing it
  with full loss-aware VOI now — it's a *deliberate* Week-1 simplification (FLAG cost 2
  is the natural ceiling on evidence spend), defensible and simple; the loss-aware
  version is logged as future work, not treated as a Week-1 defect.
- (Did not reject any point outright — the review was high-quality; the scoping to
  "future work" is the judgment call, appropriate for a Week-1 thinking-first prototype
  that the reviewer itself said "isn't the main production risk.")
- **Review 3 / P7 (partial):** accepted the *warning* (Bayesian outputs can look more
  certain than the guessed inputs justify) and added open-Q9 — but pushed back on the
  framing that the numbers are "smuggled in as fact." The document already labels every
  prior/likelihood/cost as an assumption with provenance (§3–§5), which is exactly the
  discipline the course asks for; the honest fix is to say outputs are *conditional on*
  those assumptions, not to pretend the modelling itself is illegitimate.

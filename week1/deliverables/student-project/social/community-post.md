# Community post — Weeks 1 + 2 (combined deliverable)

*For the AI-Native Engineering cohort community. First-person, in your voice. Precise
but exhaustive: states the problem, how I worked, what I found (including the humbling
bits), and ends by asking the group/instructor whether the approach is sound or
over-engineered. `[FILL]` marks the only spots you must supply so nothing is fabricated.*

---

**How I approached Weeks 1 + 2 as one combined deliverable (and some questions for the group)**

**The problem I picked** (Section 12 #11, data-quality agent, made specific):
a *Product Data Normalization Agent* for scraped e-commerce specs, scoped to consumer
electronics. It decides **per field** (RAM, storage, weight, …). One sentence:

> The agent observes a scraped product field value and must ACCEPT / REPAIR / buy more
> evidence / FLAG-FOR-HUMAN / REJECT it — because whether the value matches the
> product's *true* canonical spec is unknown.

The catch is you never see the true spec. `16000 MB` of RAM is a unit slip; `160 GB`
of RAM is an impossible typo; `512 GB` storage can be perfectly real but copied from
the wrong variant; and "5 sites agree" often just means 5 sites copied the same bad
feed.

**How I worked (Cursor as a thinking harness, not a code generator).**
I used Cursor with an AI assistant inside it as a Socratic tutor — I owned every design
call; it taught, questioned, and drafted. Early on it jumped straight to Python and I
stopped it, because the point of Week 1 (as the instructor framed it) is the *thinking*.
So we set up a deliberate structure and kept it for both weeks:

- `WORKING-CONTEXT.md` — the working agreement + a per-step ritual (teach the concept →
  I make the call → feedback → log it), so the collaboration stayed learning-first.
- A markdown **decision model** as the primary artifact; code came *after* the thinking
  was done and only to *reproduce* the numbers, never to invent them.
- Decision records + a review log so every number has provenance.

**Week 1 — belief + cost.** Six MECE hidden "worlds" (correct / unit_error /
wrong_product / typo / missing / garbled), a prior from source trust, Bayesian updates
as cheap clues arrive, then the action that **minimises expected cost** (publishing a
wrong spec is ~20× worse than flagging one). Tested on 40 labelled cases vs. a
deliberately dumb "score + threshold" baseline.

The humbling part: my version *did* have the lowest average cost (2.30 vs 3.10, and it
was statistically significant on a paired Wilcoxon test) — but the **median per-case
difference was zero**, only 9/40 decisions actually changed, and all three variants made
the *same* 2 catastrophic mistakes. Most of the "win" came from punting 57% of cases to
a human, not from being smarter.

**Week 2 — information.** I extended the same engine to ask *which clue to buy next, and
when to stop*, measured properly:
- doubt in **bits** (entropy) before/after evidence;
- rank clues by **expected information gain ÷ cost** (not the after-the-fact number);
- replace Week 1's flat "buy-twice" cap with a true **value-of-information** stop rule
  derived from the cost matrix.

Three findings I'm oddly proud of *because* they went against my first guess:
1. The **most informative** clue is **not** the best buy — the manufacturer proxy
   carries the most raw bits (0.25) but a cheaper cross-source panel wins per rupee.
2. On the worked case **every** clue has **VOI = 0** → the agent should flag now, not
   buy: an informative clue can still be decision-worthless.
3. I predicted "make the human expensive and buying revives" — **tested it, it's false.**
   VOI plateaus below the clue cost because the fallback just switches FLAG→REJECT. I
   reported the *falsified* hypothesis rather than dress it up, which felt like the more
   honest (and stronger) result.

**Where feedback actually changed the work.** The most useful input came from strangers,
not the model. Someone in a web-scraping community pointed out my "cross-source
agreement" signal was double-counting copies of the same feed — that flipped a decision
from *repair* to *flag*. A statistician reminded me experience-based priors are fine for
an internal pipeline but not a research claim. An ML practitioner handed me the test I
now lean on: "build the dumb baseline and check if the smart layer pays rent."

**Biggest lesson:** a "97% correct" that's only right 60% of the time is worthless —
calibration isn't a footnote; an overconfident "looks fine" quietly destroys the whole
cost calculation.

Everything (markdown model, runnable stdlib code that reproduces every number, the
preprint, decision + review + discussion logs) is here: [FILL: repo link]

**Questions for the group / instructor:**
1. Is combining Weeks 1 + 2 into one paper + engine the intended path, or were they
   meant to stay separate?
2. For a *learning* deliverable, is a full VOI/entropy layer the right depth — or is it
   over-engineering past the point the exercise is testing?
3. Did anyone else find their belief layer *didn't* clearly beat a calibrated
   score+threshold baseline? Curious whether that's expected or a sign I mis-scoped the
   problem.

---

## Posting notes
- Post in your own words — trim hard if your community favours shorter posts (keep:
  problem → the "median difference was zero" surprise → the falsified-hypothesis finding
  → the 3 questions).
- Put the repo link inline here (community platforms usually don't penalise links the
  way LinkedIn does).
- The three questions are the point — they invite the same discussion that improved the
  work.

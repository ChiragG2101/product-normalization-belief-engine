# Week 1 Deliverable: Product Data Normalization Belief Engine — PLAN

> This is the canonical, in-repo copy of the working plan (the IDE also keeps a
> live copy under `.cursor/plans/`). If the two ever diverge, this file plus
> `WORKING-CONTEXT.md` are the source of truth.

## Overview
Build the Week 1 "product data normalization agent" as a thinking-first markdown
decision model that mirrors the course's V0-V5 belief-engine ladder, with the
student doing the reasoning at each step and the AI giving feedback, attaching
the course's vocabulary, and recording committed decisions. Code (a small
runnable agent + experiment table) comes only after the thinking artifact is
sound.

## Todos (status tracked in the IDE plan)
1. Step 1: MECE hidden-state worlds — DONE
2. Step 2: Observations vs hidden outcome (3 layers) — DONE
3. Step 3: Counted prior / base rate; split 100 tokens — DONE
4. Step 4: Evidence + likelihoods; posterior via card-count and Bayes formula — DONE
5. Step 5: Event + random-variable mappings + asymmetric cost table — DONE
6. Step 6: Expected-loss policy, thresholds, info-buying (value of information) — DONE
7. Step 7: Experiment / test-case table (10-20 scaling to 30-50 rows) — DONE
8. Step 8: Failure analysis (>=5) + open questions — DONE
9. Step 9 (Sec 4): research-file.md (AI drafts candidates, student verifies) — DONE
10. Step 10 (Sec 10): probability-decision-record.md with full audit-data row — DONE
11. Step 11 (Sec 9, optional): runnable agent in src/ + experiment table to results/ — DONE
12. Step 12 (Sec 11): review-record.md + 3 reviews run + adjudicated (all 3 lenses) — DONE
13. Step 13 (Sec 13): LaTeX preprint (12 sections) + compile preprint.pdf — DONE
    (paper/preprint.tex + references.bib + preprint.pdf [12 pp], compiled with tectonic)
14. Step 14 (Sec 14): linkedin-post.md + x-thread.md drafts — DONE (drafts; author publishes)
- Sec 5-7 (student-only): real Reddit/X discussions + discussion-record.md — DONE (5 logged;
  volume/breadth bar = author action)
- Finalize: README repro + AI-USE.md + COMPLETION-CHECKLIST.md — DONE
  (open items are author actions only: hit Reddit/X volume bar + publish the drafts)

## The problem (locked)
"The agent observes a scraped product field value. It must ACCEPT, REPAIR, buy
more evidence (re-scrape / query manufacturer), FLAG-FOR-HUMAN, or REJECT it
because whether the value matches the product's true canonical specification is
not known." Domain: consumer electronics (phones/laptops). Granularity: per field.

## Directory layout (matches Section 15 spec)
Required nesting `week1/deliverables/student-project/` with empty required folders
(`paper/figures/`, `src/`, `data/`, `experiments/`, `results/`, `social/`,
`decisions/`) carrying `.gitkeep`. Existing files: `README.md`,
`WORKING-CONTEXT.md`, `PLAN.md`, `.gitignore`,
`decisions/belief-engine-decision-model.md` (+ `.venv`, git-ignored).

## File-creation timing
Create each CONTENT file only at the step where it belongs (avoid stale hollow
placeholders). Empty required FOLDERS may exist now. Mapping: research-file.md
after Steps 1-2; probability-decision-record.md at Step 10; discussion-record.md
when real Reddit/X happens; src/data/experiments/results only if code is built;
paper/* at the LaTeX step; review-record.md at the review step; social/* at the
publishing step; README finalized at the end.

## The per-step ritual (HOW we run every step) — MANDATORY ORDER
1. Re-ground: re-read `WORKING-CONTEXT.md` (step log + glossary).
2. Teach the concept FIRST, before any question: (a) theory in plain language,
   (b) tie to the specific course example/chapter, (c) what we achieve + why it
   matters later.
3. Ask open, paragraph-style questions that force the student to reason.
4. Wait for the student's answer in their own words.
5. Give honest feedback (right/partial/off + where agentic thinking needs
   sharpening) and attach the course's proper name ("work before the name").
6. Commit + record: only after the student commits, write the section into
   `decisions/belief-engine-decision-model.md`, append a receipt to the step log,
   add any new term to the glossary.
7. Advance: mark the todo complete and move to the next step, restarting at 1.

## Step sequence

### Step 1 — MECE worlds (Ch.1)
Crisp, non-overlapping definitions for the 6 worlds: correct / unit_error /
wrong_product / typo / missing / garbled. Mutually exclusive + collectively
exhaustive (`garbled` is the "something-else" box).

### Step 2 — Observations (Ch.1: three layers)
List what the agent observes vs the hidden outcome. Separate hidden reality /
observations / belief. Note already-have vs go-buy evidence.

### Step 3 — Counted prior / base rate (Ch.2)
Source-reliability prior from a stated comparable pile (labeled assumption + a
receipt). Split 100 tokens across the worlds. Guard against the base-rate trap.

### Step 4 — Evidence + likelihoods + Bayes update (Ch.2)
Pick an evidence signal; estimate P(evidence | each world); compute the posterior
BOTH as a 100-card count and via prior x likelihood / normalise.

### Step 5 — Event + random variable + cost table (Ch.1 & Ch.5)
Map worlds -> stakeholder yes/no questions (events) -> action values. Build the
asymmetric cost table (relative costs with rationale + owner of each cost).

### Step 6 — Policy: expected loss, thresholds, info-buying (Ch.5)
Action rule = smallest expected loss; derive thresholds from cost ratios; add
info-buying actions governed by value-of-information; Act/Ask/Hold/Escalate +
stop-asking rule.

### Step 7 — Experiment / test-case table
10-20 (scaling to 30-50) cases spanning worlds and evidence combos. Each row:
evidence -> updated belief -> event value -> chosen action -> outcome + cost.
Hide the label at decision time.

### Step 8 — Failure analysis + open questions (Ch.0 cost lens)
Examine >=5 wrong/fooled decisions; name each failure mode; state which error is
highest-cost and to whom; list 3+ honest "what it can't do" open questions.

## Full-deliverable steps (after Steps 1-8)
- Step 9 (Sec 4): `research-file.md` — terms, queries, candidate Reddit/X
  communities (with why-relevant), candidate X accounts, 5 candidate
  papers/repos/datasets, questions, AI prompts + AI errors. AI drafts candidates
  marked "unverified"; student verifies/prunes.
- Step 10 (Sec 10): `decisions/probability-decision-record.md` with full
  audit-data row (time, data version, model version, policy version) + prior ->
  evidence -> likelihood -> posterior -> threshold -> new action.
- Step 11 (Sec 9, optional): small agent in `src/` mirroring the model; 30-50
  simulated labeled cases in `data/`; 2 policies + 1 baseline (labels hidden);
  predictions/metrics to `results/` (confusion matrix, precision/recall,
  human-review rate, decision cost, calibration).
- Step 12 (Sec 11): `review-record.md` + THREE ready-to-paste review prompts
  (practitioner / probability / preprint). Student runs them elsewhere; AI does
  not fabricate reviews.
- Step 13 (Sec 13): `paper/main.tex` (12 sections) + `references.bib` from real
  results; compile `paper/preprint.pdf` (needs LaTeX installed — none detected
  yet). Include AI-use statement + contribution statement (if team). No invented
  citations.
- Step 14 (Sec 14): `social/linkedin-post.md` + `social/x-thread.md` drafts from
  real results; student publishes.

## Student-only work (Sec 5-7) — never fabricated by AI
Real Reddit (>=10 contributions across >=5 communities, >=5 discussions) and X
(21-28 comments over 7 days, >=3 discussions). AI provides `discussion-record.md`
structure and can summarize the student's real discussions; the contributions and
human replies must be genuinely the student's. Placeholders until done.

## Finalize
README reproduce instructions (if code exists), AI-use statement, and a pass over
the Section 16 completion checklist to confirm evidence for: "The student used AI
tools and human discussions to make, test, improve, and publish new technical
information about one problem."

---

## Week 2 (combined) — Information layer

Decision: extend the Week-1 belief engine in place (same problem, worlds, costs,
worked 160 GB case) with Week-2's information-theory layer; fold everything into ONE
combined 13-section preprint (retitled) + a 20-question appendix. Thinking-first in
markdown, then paper; code changes deferred (existing `src/` still runs).

Full roadmap + step log live in `WORKING-CONTEXT.md` §W2.

- W2-1 Setup: install `week2-readiness`/`week2-coach` skills; write narrowed research
  question ("which clue next, when to stop, by expected info per unit cost") into
  model §0.1 + paper intro/abstract — DONE
- W2-2 Entropy before/after on 160 GB (model §9): prior 2.123 → post-oos 1.880 bits;
  clue flips leader but barely cuts doubt; expected (0.228) vs observed (0.243) gain
  — DONE
- W2-3 Which clue next / bits-per-cost (model §10): 3 author-set costed clues;
  manufacturer most informative (0.250) but cross-source panel wins per rupee
  (0.135 > 0.125) — raw-bits vs per-cost rankings DISAGREE; stale reference ≈ worthless
  (0.039) — DONE
- W2-4 True VOI stop rule (model §11) replacing the flat 2-buy cap: on 160 GB EVERY
  clue VOI=0 (even the most-informative) → flag now (different from Week-1);
  VOI-positive only near ACCEPT/FLAG frontier — DONE
- W2-5 Critical-thinking challenge (model §12): highest-info ≠ best buy (two ways);
  "evidence raises uncertainty" HONESTLY DROPPED — all branches lower entropy on our
  numbers; kept a note on when it would trigger — DONE
- W2-6 `decisions/information-decision-record.md`: one worked which-clue-next +
  when-to-stop audit trail — DONE
- W2-7 Generalization + new questions (model §13): FALSIFIED hypothesis — making the
  human expensive (FLAG 2→15) does NOT revive buying (VOI plateaus 0.38/0.23,
  fallback switches FLAG→REJECT@4.21); 4 new questions from our own info results — DONE
- W2-8 Combined preprint (`paper/preprint.tex`, retitled): new §7 information layer
  with entropy figure + clue-ranking + VOI tables; 20-question appendix; compiles
  clean via tectonic (only cosmetic overfull warnings) — DONE
- W2-9 Docs: WORKING-CONTEXT §W2, this PLAN, README, COMPLETION-CHECKLIST updated —
  DONE

Author-only remaining (unchanged from Week 1, never fabricated by AI): publish the
social drafts and hit the Reddit/X volume-and-breadth bar; optionally run three fresh
adversarial AI reviews of the information layer.

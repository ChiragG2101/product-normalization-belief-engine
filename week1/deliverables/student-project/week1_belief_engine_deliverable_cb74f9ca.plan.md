---
name: Week1 Belief Engine Deliverable
overview: Build the Week 1 "product data normalization agent" as a thinking-first markdown decision model that mirrors the course's V0-V5 belief-engine ladder, with you doing the reasoning at each step and me giving feedback, attaching the course's vocabulary, and recording your committed decisions. Code (a small runnable agent + experiment table) comes only after the thinking artifact is sound.
todos:
  - id: worlds
    content: "Step 1: Pin down MECE hidden-state worlds with crisp non-overlapping definitions"
    status: completed
  - id: obs
    content: "Step 2: List observations vs hidden outcome (3 layers: reality/observation/belief)"
    status: in_progress
  - id: prior
    content: "Step 3: Counted prior/base rate with receipt; split 100 tokens into starting board"
    status: pending
  - id: bayes
    content: "Step 4: Evidence + likelihoods; compute posterior as card-count and via Bayes formula"
    status: pending
  - id: cost
    content: "Step 5: Event + random-variable mappings + asymmetric cost table"
    status: pending
  - id: policy
    content: "Step 6: Expected-loss policy, thresholds, info-buying actions (value of information)"
    status: pending
  - id: experiment
    content: "Step 7: Build the experiment/test-case table (10-20 scaling to 30-50 rows)"
    status: pending
  - id: failures
    content: "Step 8: Failure analysis (>=5) + honest open questions"
    status: pending
  - id: research_file
    content: "Step 9 (Sec 4): research-file.md - terms, queries, candidate Reddit/X communities, 5 papers, questions; AI drafts candidates, student verifies"
    status: pending
  - id: prob_record
    content: "Step 10 (Sec 10): probability-decision-record.md with full audit-data row (time/data/model/policy version)"
    status: pending
  - id: code_optional
    content: "Step 11 (Sec 9, optional): small runnable agent in src/ that mirrors the model + emits the experiment table to results/"
    status: pending
  - id: reviews
    content: "Step 12 (Sec 11): review-record.md + ready-to-paste practitioner/probability/preprint review prompts for student to run in ChatGPT/Gemini"
    status: pending
  - id: preprint
    content: "Step 13 (Sec 13): LaTeX preprint (12 sections) in paper/main.tex + references.bib from real results; compile preprint.pdf (needs LaTeX installed)"
    status: pending
  - id: social
    content: "Step 14 (Sec 14): social/linkedin-post.md + x-thread.md drafts from real results; student publishes"
    status: pending
  - id: human_discussions
    content: "Sections 5-7 (student-only): discussion-record.md structure; real Reddit/X discussions + publishing done by student, never fabricated"
    status: pending
  - id: finalize
    content: "Finalize: README repro instructions, AI-use statement, completion checklist (Sec 16) verification"
    status: pending
isProject: false
---

# Week 1 Deliverable: Product Data Normalization Belief Engine

## Working agreement (how we run every step)
1. I ask you open questions first; you reason in your own words.
2. I tell you honestly if your thinking is right / partial / off, and where your *agentic thinking* needs sharpening.
3. I attach the course's proper name to what you reasoned ("work before the name").
4. Once you commit, I write it into the markdown artifact; you own the numbers, I sanity-check and flag any "guess wearing a lab coat."
5. Code stays optional and comes late. The Week 1 win is the thinking artifact + an experiment/test-case table.

## The problem (locked)
"The agent observes a scraped product field value. It must ACCEPT, REPAIR, buy more evidence (re-scrape / query manufacturer), FLAG-FOR-HUMAN, or REJECT it because whether the value matches the product's true canonical specification is not known." Domain: consumer electronics (phones/laptops). Granularity: per field.

## Directory layout (matches Section 15 spec)
The required nesting `week1/deliverables/student-project/` is restored to match the deliverable spec exactly. Empty required folders exist now (`paper/figures/`, `src/`, `data/`, `experiments/`, `results/`, `social/`, `decisions/`) with `.gitkeep`. Existing files: `README.md`, `WORKING-CONTEXT.md`, `.gitignore`, `decisions/belief-engine-decision-model.md` (+ `.venv`, git-ignored).

## File-creation timing (added at student request)
Create each CONTENT file only at the step where it belongs (born when it has real content), to avoid stale hollow placeholders. Empty required FOLDERS may exist now (harmless, satisfies Section 15). Mapping: research-file.md after Steps 1-2; probability-decision-record.md at Step 10; discussion-record.md when real Reddit/X happens; src/data/experiments/results only if code is built; paper/* at the LaTeX step; review-record.md at the review step; social/* at the publishing step; README finalized at the end.

## The artifact we build first
A single markdown decision model: `week1/decisions/belief-engine-decision-model.md` (working title), structured to mirror the course ladder and to satisfy the assignment's Sections 3, 8, 9, 10. It will contain: problem statement, observations, MECE hidden-state worlds, counted prior (with receipts), evidence + likelihoods, belief update (Bayes, shown as card-counts AND formula), event/random-variable mappings, cost table, expected-loss policy with thresholds, info-buying actions with value-of-information reasoning, a 10-20 (up to 30-50) row experiment/test-case table, and 3+ failures/open questions.

## Documentation discipline (added at student request)
Two persistent docs back this work so nothing is lost to context limits:
- `WORKING-CONTEXT.md` (project root): session memory - what we target, the working-agreement rules, how the student approaches it, how the AI must question the student, the step ladder, a concepts-learned glossary, and a running step log (receipts of each decision + why).
- `decisions/belief-engine-decision-model.md`: the graded thinking artifact itself.
The AI re-reads `WORKING-CONTEXT.md` at the start of each step and appends the step's receipts to its step log after the student commits.

## Concept-teaching discipline (added at student request)
The student has not been through every part of the course, so concept-teaching is mandatory at each step. Each taught concept is recorded in the `WORKING-CONTEXT.md` glossary with its course example and where we used it.

## The per-step ritual (HOW we run every step) - MANDATORY ORDER
Every step follows this exact sequence (never jump straight to questions):
1. Re-ground: re-read `WORKING-CONTEXT.md` (step log + glossary).
2. Teach the concept FIRST, before any question: (a) explain it theoretically in plain language, (b) tie it to the specific course example/chapter it came from, (c) state what we achieve by it and why it matters for later steps.
3. Ask open, paragraph-style questions that force the student to reason it out for their problem.
4. Wait for the student to answer in their own words.
5. Give honest feedback (right/partial/off + where agentic thinking needs sharpening) and attach the course's proper name to what they reasoned.
6. Commit + record: only after the student commits, write the section into `decisions/belief-engine-decision-model.md`, append a receipt to the step log, and add any new term to the glossary.
7. Advance: mark the todo complete and move to the next step, restarting at 1.
This ritual is mirrored in `WORKING-CONTEXT.md` section 4a.

## Step sequence (each is a "work before the name" cycle)

### Step 1 - Nail the MECE worlds (Chapter 1 discipline)
Pin down crisp, non-overlapping definitions for the ~5 hidden-state worlds: correct-value / unit-error / wrong-product-value / typo / missing. Ensure mutually exclusive + collectively exhaustive (add a "something-else" box if needed). Deliverable: the "possible worlds" section.

### Step 2 - Observations (what the agent can vs cannot see)
List what the agent observes (raw value, field name, source, other sources' values, format) vs the hidden outcome. Separate the three layers the course insists on: hidden reality / observations / belief. Deliverable: the "observations" section.

### Step 3 - Counted prior / base rate (Chapter 2 discipline)
You choose a source-reliability prior FROM a stated comparable pile (even if simulated), labeled as an assumption with a receipt. Split 100 tokens across the worlds as the starting board. Guard against the base-rate trap. Deliverable: prior belief board + provenance.

### Step 4 - Evidence + likelihoods, then the Bayes update (Chapter 2)
Pick one real evidence signal (e.g. cross-source agreement or plausibility). You estimate P(evidence | each world). We compute the posterior BOTH as a 100-card count and via prior x likelihood / normalise. This directly produces the assignment's Section 10 probability decision record. Deliverable: worked posterior for one uncertain case.

### Step 5 - Event + random variable + cost table (Chapters 1 and 5)
Map worlds -> stakeholder yes/no questions (events) -> action values. Build the asymmetric cost table (you set the relative costs with rationale + owner of each cost). Deliverable: cost table + event mappings.

### Step 6 - Policy: expected loss, thresholds, and info-buying (Chapter 5)
Define the action rule as "smallest expected loss," derive thresholds from the cost ratios, and add the info-buying actions (re-scrape / query manufacturer) governed by value-of-information ("buy only if expected saving > cost"). Include Act / Ask / Hold / Escalate + a stop-asking rule. Deliverable: the policy section.

### Step 7 - Experiment table (the output artifact, like the submission you admired)
Build 10-20 (scaling toward 30-50) test cases spanning the worlds and evidence combinations. Each row: evidence -> updated belief -> event value -> chosen action -> (later) outcome + cost. Hide the label at decision time. Deliverable: the experiment/test-case table.

### Step 8 - Failure analysis + open questions (Chapter 0 cost lens)
Examine >=5 cases where the agent decides wrong or is fooled; name each failure mode; state which error is highest-cost and to whom; list 3+ honest "what it can't do" open questions (like the influencer submission's honest tab). Deliverable: failures section.

## Full-deliverable steps (after the thinking artifact, Steps 1-8, is done)

### Step 9 - Research file (Section 4)
Create `research-file.md` recording: problem statement, objective, experience level, technical terms, useful search queries, 5-10 CANDIDATE Reddit communities (with why-relevant), CANDIDATE X accounts, and 5 candidate papers/repos/datasets. Rule: AI drafts candidates and clearly marks them "unverified - student must verify"; the student verifies/prunes. Also record AI prompts used and important AI errors, per the spec.

### Step 10 - Probability decision record (Section 10)
Create `decisions/probability-decision-record.md` for one uncertain case, with the full audit-data row the spec requires (time, data version, model version, policy version) plus prior -> new evidence -> likelihood -> posterior -> threshold -> new action. Derived from Step 4's worked case but formatted to the Section 10 table.

### Step 11 - Optional runnable agent (Section 9)
Only if desired: a small agent in `src/` that mirrors the decision model (belief update + expected-loss policy), generates 30-50 simulated labeled cases in `data/`, runs 2 policies + 1 baseline hiding labels at decision time, and writes predictions/metrics to `results/`. Provides the confusion matrix, precision/recall, human-review rate, decision cost, calibration. Code is optional per the course; the experiment table (Step 7) can stand alone if we skip code.

### Step 12 - AI reviews (Section 11)
Create `review-record.md` with the spec's table and THREE ready-to-paste review prompts (practitioner / probability / preprint). The student runs these in ChatGPT/Gemini/Spark and pastes results; AI does not fabricate reviews. Student records accept/reject + reason per comment.

### Step 13 - LaTeX preprint (Section 13)
Write `paper/main.tex` (12 required sections) + `references.bib` using ONLY real numbers pulled from the experiment table / results. Compile to `paper/preprint.pdf`. Needs a LaTeX toolchain installed (none detected yet - will surface install options at this step). Include the AI-use statement and (if team) contribution statement. No invented citations; each reference must be one the student actually read.

### Step 14 - Publish (Section 14)
Draft `social/linkedin-post.md` (problem, why this design, why this probability model, one key result/failure, one design change from a discussion, biggest limitation, one specific ask) and `social/x-thread.md` (problem, test, result, open question). Student publishes; drafts use only real results with placeholders for anything requiring the student's own voice/links.

## Student-only work (Sections 5-7) - never fabricated by AI
Real Reddit contributions (>=10 across >=5 communities, >=5 discussions) and X comments (21-28 over 7 days, >=3 discussions). AI creates the `discussion-record.md` structure and can summarize/structure the student's real discussions afterward, but the contributions and human replies must be genuinely the student's. These are recorded as clearly-marked placeholders until done.

## Finalize
README reproduce instructions (if code exists), AI-use statement, and a pass over the Section 16 completion checklist to confirm evidence for: "The student used AI tools and human discussions to make, test, improve, and publish new technical information about one problem."

## Reset note
The earlier auto-generated Python core logic was cleared; the belief-engine decision model is the center of gravity. Required Section-15 folders are restored (empty, with .gitkeep) and content files are created at their step.
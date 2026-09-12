# Section 16 — Completion Checklist

The deliverable must show evidence for one claim:

> **"The student used AI tools *and* human discussions to *make, test, improve, and
> publish* new technical information about *one* problem."**

Below, each part of that claim is mapped to concrete evidence in this repo. Items that
depend on the author's own account activity (publishing) are marked **AUTHOR ACTION**
so nothing is falsely claimed as done.

## One problem (scope)
- [x] A single, clearly-scoped problem: per-field publish/repair/flag/reject decision
      for scraped e-commerce product specs when the true spec is unknown.
      → `README.md`, `decisions/belief-engine-decision-model.md` §0.

## Used AI tools
- [x] AI used as a Socratic tutor + pair (concepts taught, decisions owned by author).
      → `AI-USE.md`, full trail in `WORKING-CONTEXT.md`.
- [x] Three adversarial AI reviews run across different models, each comment
      adjudicated. → `review-record.md`.

## Used human discussions
- [x] Real discussions with real people, logged with links + takeaways.
      → `discussion-record.md` §5 (5 discussions across Reddit communities).
- [x] ≥1 concrete design change *from* a discussion (required).
      → correlated-sources point → policy 1.0 → 1.1 → a decision flips REPAIR → FLAG.
      `decisions/probability-decision-record.md`; decision model §8 (F2).
- [ ] **AUTHOR ACTION — breadth/volume bar:** Reddit ≥10 contributions across ≥5
      communities / ≥5 discussions, and X ~21–28 comments over 7 days / ≥3 discussions.
      Qualitative bar (a discussion improved the work) is **met**; remaining gap is
      volume/breadth on the author's accounts. Track in `discussion-record.md`.

## Made new technical information
- [x] A decision model that is more than a restatement: six MECE worlds + Bayesian
      belief + asymmetric-cost expected-loss policy + info-buying + human abstain.
      → `decisions/belief-engine-decision-model.md`.
- [x] A runnable implementation. → `src/` (domain, agent, data gen, evaluate).

## Tested it
- [x] Evaluation on 40 labelled cases (labels hidden at decision time), against an
      autonomous variant and a dumb baseline. → `data/cases.jsonl`, `results/`.
- [x] Metrics beyond accuracy: decision cost, human-review rate, wrong-publish count,
      accept precision/recall, calibration bins, belief-vs-baseline agreement, and a
      paired Wilcoxon significance test. → `results/metrics.json`, `results/report.md`.
- [x] Deliberate failure seeds + a documented failure analysis. → decision model §8.

## Improved it (loop closed)
- [x] Design changes traceable to feedback: correlated-evidence discount (human
      discussion); calibration reframed as decision-inverting, "earns its keep"
      retracted, conditional-independence stated, VOI relabeled a budget heuristic,
      significance test added (AI reviews). → `review-record.md` change log; decision
      model §3.2, §4.6, §6.2–§6.3, §7, §8.
- [x] Honesty maintained: assumptions labelled, no fabricated reviews/discussions/
      citations, limitations + threats-to-validity documented. → preprint §5, §10, §11.

## Published new technical information
- [x] A written-up preprint with methods, results, limitations, related work, and an
      AI-use statement. → `paper/preprint.pdf` (combined 13 sections + 20-question
      appendix), `AI-USE.md`.
- [x] Publish-ready social drafts grounded in the real results. → `social/`.
- [ ] **AUTHOR ACTION — actually publish** the LinkedIn post and X thread (and, if
      desired, push the repo to a public remote and drop the link in).

## Week 2 — information layer (combined deliverable)
- [x] Uncertainty measured in **bits** (entropy) before/after evidence on the worked
      case. → decision model §9; preprint §7; figure in the paper.
- [x] Evidence chosen by **expected information gain per unit cost** (≥3 real costed
      clues), using expected — not observed — gain. → model §10; preprint Table (clues).
- [x] Explicit **value-of-information** stop rule replacing the flat cap, derived from
      the cost matrix. → model §11; preprint §7.4 + VOI table.
- [x] Every Week-2 number (entropy, bits-per-cost ranking, VOI, the falsified
      FLAG-sweep) reproduced from **committed code**, not a scratch script.
      → `src/information.py` (stdlib; reuses `domain.py`/`agent.py`).
- [x] Critical-thinking challenge with our own numbers: highest-info ≠ best buy (two
      ways). The "evidence *raises* uncertainty" intuition was tested and **honestly
      dropped** — all clue branches lower entropy on our numbers; we kept a note on
      *when* it would trigger rather than manufacture a row. → model §12; preprint §7.6.
- [x] Generalization tested as a **falsified hypothesis**: making the human expensive
      does *not* revive buying (VOI plateaus below clue cost; fallback switches
      FLAG→REJECT). → model §13.1; preprint §7.8.
- [x] One worked **information decision record** (which clue next / when to stop).
      → `decisions/information-decision-record.md`.
- [x] Generalization (one environment change: expensive/fallible human) + new
      questions from our own results. → model §13; preprint conclusion.
- [x] The **20 required core questions** answered in an appendix. → preprint App. A.
- [ ] **AUTHOR ACTION (optional but recommended):** run three fresh adversarial AI
      reviews of the information layer, and publish a Week-2 social post.

## Summary
Everything the author can complete alone (make / test / improve / write up) is
**done and evidenced** for both weeks. The only open items are **author actions**:
hitting the Reddit/X *volume* bar, *publishing* the drafts, and (optionally) running
fresh reviews of the Week-2 information layer. Once done, tick the boxes and add the
links to `discussion-record.md` / the social drafts.

# AI-Use Statement

This deliverable was built **collaboratively with an AI assistant**, used deliberately
as a Socratic tutor and pair-programmer rather than a ghostwriter. This statement
records honestly what the AI did, what the author did, and where the evidence lives.

## Tools used
- **Claude (via the Cursor IDE harness)** — primary collaborator for teaching concepts,
  asking clarifying questions, and drafting files.
- **ChatGPT, Claude, and Gemini** — used independently to run three adversarial reviews
  of the work (one model per review lens, in separate fresh sessions).

## What the AI did
- Explained the underlying concepts step by step (hidden state, priors, likelihoods,
  Bayes' rule, expected loss, calibration, reject-option, value of information) with
  worked examples, on request.
- Asked clarifying questions at each step and pushed back on inconsistent reasoning
  (e.g. an early prior that implied 70% of values were flawed before looking).
- Drafted the markdown decision model, the runnable Python agent, the evaluation
  harness, the LaTeX preprint, and these supporting documents — always from decisions
  the author had already made.
- Implemented a paired significance test in direct response to a reviewer's challenge.

## What the author owned (every design decision)
- The six MECE worlds and the tie-breaker between them.
- The three source-reliability priors and their token splits.
- The cost ordering and the asymmetric cost matrix values.
- The ACCEPT threshold (95%) and the 2-buy budget cap.
- Which review comments to accept vs. reject, and why (adjudicated in
  `review-record.md`).
- All real human-community engagement (the discussions in `discussion-record.md` are
  genuinely the author's; the AI only drafted opening posts and structured the log).

## Reviews and how feedback was handled
Three adversarial AI reviews were run — **practitioner** (ChatGPT), **probability /
statistics** (Claude), and **preprint / writing** (Gemini) — each in its own fresh
session. Every comment was adjudicated with an accept/reject decision and a reason, and
accepted comments produced real edits. Notable outcomes (full log in
`review-record.md`):
- The probability review **validated** the core Bayesian mechanics and surfaced an
  unstated conditional-independence assumption in evidence chaining.
- The preprint and practitioner reviews forced honesty corrections: the "belief layer
  earns its keep" claim was **retracted** in favor of a narrower one, and the top-bin
  miscalibration was reframed as a decision-inverting problem rather than a footnote.

## Human discussions (the non-AI half)
Five real online discussions (Reddit) measurably changed the design — most importantly,
a web-scraping practitioner's point that "sources agreeing" is not independence became
the correlated-evidence discount (policy 1.0 → 1.1), which flipped one decision from
REPAIR to FLAG. Links, summaries, and "wired into" pointers are in
`discussion-record.md`.

## Honesty commitments
- No fabricated reviews, discussions, or citations. The preprint's bibliography cites
  only real works; ideas from discussions or the course are attributed in-text.
- Assumptions are labelled as assumptions with their provenance; only the evaluation
  results are presented as measured facts.
- The full conversation and decision trail is preserved in `WORKING-CONTEXT.md`.

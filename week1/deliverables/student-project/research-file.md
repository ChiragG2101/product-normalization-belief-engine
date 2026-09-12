# Research File — Product Data Normalization Belief Engine (Week 1, Section 4)

> Verification legend: **[verified]** = the AI opened the page and confirmed it;
> **[unverified]** = surfaced by web search only — the STUDENT must open and confirm
> it before citing; **[verify while logged in]** = login-walled (Reddit/X/LinkedIn),
> confirm from your own account. Nothing here is a citation of a *response*; the
> discussion citations (Sections 5–7) come later from real posts you make.

---

## 1. Problem statement
The agent observes a scraped product field value and must ACCEPT, REPAIR, buy more
evidence (re-scrape / query manufacturer), FLAG-FOR-HUMAN, or REJECT it, because
whether the value matches the product's true canonical specification is not known.
Domain: consumer electronics (phones/laptops). Granularity: one decision per field.

## 2. Objective
Build a per-field **belief engine** that decides, under uncertainty, whether a
scraped product-spec value is safe to publish — choosing among ACCEPT / REPAIR /
BUY-evidence / FLAG-FOR-HUMAN / REJECT — **so that** wrong specs don't reach
customers while good data is not needlessly discarded or sent to humans.

## 3. Experience level (author self-assessment)
- Probability / Bayesian reasoning: **beginner**.
- Building agents: **beginner**.
- Software engineering: **3+ years, full-stack engineer** (strong general SWE).
- Implication: framing is "an experienced software engineer learning the
  probabilistic-agent side" — useful context when asking communities for feedback.

## 4. Technical terms (from the decision model glossary)
Three layers (hidden reality / observation / belief); MECE worlds; support of a
distribution; decision-relevance / information gain; observation vs. clue
("don't mark your own paper"); prior / base rate + provenance ("receipts");
base-rate trap; likelihood `P(clue | world)`; Bayes update (prior × likelihood,
normalize); posterior + chaining; event / random variable; asymmetric cost + who
pays; expected loss + smallest-loss rule; derived thresholds; value of information
(VOI) + cost-cap stop rule. (Full definitions in `WORKING-CONTEXT.md` §6.)

## 5. Useful search queries
- "cost-sensitive classification Bayes risk minimum expected loss"
- "Bayesian decision theory reject option abstaining classifier"
- "product entity matching / entity resolution e-commerce benchmark"
- "attribute value normalization unit conversion product data"
- "data quality validation pipeline schema mismatch scraped data"
- "classifier with abstention / human-in-the-loop review threshold"
- "probability calibration cost matrix decision threshold"

## 6. Candidate communities to post in / learn from (Reddit)
*(All Reddit links are [verify while logged in] — confirm activity/rules yourself.)*
- **r/dataengineering** — pipelines, data quality strategies, architecture-decision
  posts; strong fit for "here's my data-quality decision model." Best-fit primary.
- **r/datascience** — methodology, probabilistic modeling, honest "real failures"
  posts perform well.
- **r/MachineLearning** — for the cost-sensitive / Bayesian-decision angle (has
  strict self-promo rules; read them).
- **r/WebScraping** — the scraping side (where the messy data originates).
- **r/WebScrapingInsider** — newer, professional, "real failures & benchmarks"
  ethos; good for the data-quality-of-scraped-data angle.
- **r/dataanalysis** — feedback on methodology and framing.

## 7. Candidate accounts to follow / engage (X, LinkedIn)
*([verify while logged in] — I did not log in; confirm these exist and are active.)*
- **[unverified]** Charles Elkan — author of "The Foundations of Cost-Sensitive
  Learning"; foundational to our expected-loss policy.
- **[unverified]** Christian Bizer / Ralph Peeters (Univ. Mannheim, WDC) — product
  entity matching / data integration.
- **[unverified]** Practitioner hashtags/topics to search rather than accounts:
  `#dataquality`, `#dataengineering`, `#entityresolution`, `#MLOps`.
- Note: pick real accounts you actually read; do not cite an account you haven't
  engaged with.

## 8. Papers / repos / datasets to read (background)
- **[verified]** *WDC Products: A Multi-Dimensional Entity Matching Benchmark* —
  Peeters, Der, Bizer, arXiv:2301.09521 (2023). Directly relevant: heterogeneous
  product records across many sources; "same attribute under different names /
  formats" is exactly our F3 failure mode.
  https://arxiv.org/abs/2301.09521
- **[unverified]** *The Foundations of Cost-Sensitive Learning* — Charles Elkan
  (IJCAI 2001). The theoretical backbone of §5–§6: optimal decisions minimize
  expected cost, and MAP is optimal *only* under 0-1 loss. (Search-surfaced;
  full text saved during research — confirm the canonical citation.)
- **[unverified]** *MaDI-Bench: An End-to-End Data Integration Benchmark* — arXiv
  (2606.30371 per search; **verify the ID/date**, looks future-dated). Covers
  schema matching + normalization taxonomies for units/capacities — mirrors our
  problem end to end.
- **[unverified]** WDC Product Data Corpus / LSPM gold standard (webdatacommons.org)
  — large real scraped-product corpus; candidate data source for the optional code
  (Step 11). (Site returned a transient error in the sandbox; reachable normally.)
- **[unverified]** C.K. Chow, *On optimum recognition error and reject tradeoff*
  (1970) — classic origin of the "reject / abstain" option = our FLAG action.

## 9. AI prompts used (record for the deliverable)
- Step-by-step Socratic build of the decision model (worlds → observations → prior
  → Bayes update → cost → policy → experiment → failures), with the AI teaching each
  concept, asking open questions, then recording committed decisions.
- Intuition-first re-teach of Bayes' rule (cough/doctor story) before any formula.
- This research step: web-search + browser-verify real communities/papers, marked
  by verification status.
- Full running log of prompts/decisions lives in `WORKING-CONTEXT.md` (step log).

## 10. Notable AI errors / corrections (honesty record)
- AI initially went code-first; reset to thinking-first per instructor guidance.
- AI blurred "observation" vs "clue"; corrected to: same thing (Layer 2), the real
  line is clue (L2) vs. true answer (L1); manufacturer spec page is a *proxy*.
- AI's first per-buy "value of information" stop rule was hard to operationalize;
  student re-derived a cost-cap rule (never spend > FLAG's cost) — adopted.
- AI overstated its abilities: it **cannot** install MCP connectors/skills or post
  to social accounts; posting is student-only (Sections 5–7).
- Search surfaced a possibly future-dated arXiv ID (MaDI-Bench) — flagged for the
  student to verify rather than cite blindly.

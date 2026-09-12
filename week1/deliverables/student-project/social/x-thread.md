# X (Twitter) thread — Week 1 deliverable

*Draft to publish in your own voice. Keep each tweet under ~280 chars. Put the repo
link in the LAST tweet only (links mid-thread suppress reach). For a small account,
the thread is secondary — the higher-leverage move is replying to others in
#buildinpublic / data / ML threads for a few days first, then dropping this.*

---

## Thread

**1/**
after you scrape product specs, how do you know a value is safe to publish?

you never see the "true" spec. so:
• 16000 MB RAM = unit slip
• 160 GB RAM = impossible typo
• 512 GB storage = real, but wrong variant
• "5 sites agree" = 5 sites copied the same bad feed

**2/**
so I stopped treating it as classification.

each value is one of 6 hidden "worlds" (correct / unit error / wrong product / typo /
missing / garbled). start from a prior based on source trust, update with Bayes as
clues arrive.

**3/**
then pick the action — accept / repair / buy more evidence / flag to a human / reject
— by *minimum expected cost*.

key: publishing a wrong spec is ~20x costlier than flagging it. that asymmetry, not
raw probability, should drive the decision.

**4/**
I tested it on 40 labelled cases vs a deliberately dumb "score + threshold" baseline.

the humbling result 👇

**5/**
✅ my version had lower avg cost (2.30 vs 3.10, statistically significant)
❌ but median per-case difference = 0. only 9/40 cases changed.
❌ all 3 versions made the SAME 2 catastrophic mistakes
❌ the win came from punting 57% of cases to a human, not from being smarter

**6/**
the best feedback came from strangers, not the model:

a scraping dev pointed out my "sources agree" signal was double-counting copies of one
feed → flipped a decision from repair → flag.

that one comment changed the design.

**7/**
biggest lesson: a "97% correct" score is worthless if it's right only 60% of the time.

calibration isn't a footnote — an overconfident "looks fine" quietly breaks the entire
expected-cost math. it can literally invert the decision.

**8/**
built with an AI assistant as a Socratic tutor — I owned every design call, it taught +
questioned + drafted. wrote it up as a mini-preprint with the ugly limitations left in.

what signals do YOU trust to catch bad data after a scrape?

repo + write-up: https://github.com/ChiragG2101/product-normalization-belief-engine

---

## Posting notes
- 8 tweets; trim to 5 if you want (1 → 5 → 6 → 7 → 8 still tells the whole story).
- Only the last tweet has a link.
- For a ~200-follower account: spend 2–3 days replying substantively in others'
  data/ML/#buildinpublic threads BEFORE posting this, so the thread lands on a
  slightly warmed-up account.
- Reply to anyone who engages within the first hour — that's where threads live or die.
- The tweet-6 "one comment changed the design" is your strongest hook if you want to
  lead with it as a standalone quote-tweet later.

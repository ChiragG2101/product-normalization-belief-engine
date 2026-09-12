# LinkedIn post — Week 1 deliverable

*Draft to publish in your own voice. One post + a first comment (LinkedIn suppresses
reach on posts with outbound links in the body, so the repo link goes in the first
comment, not the post). Swap in your real repo URL where marked.*

---

## Post (body)

I spent this week building something small and being surprised by how humbling it was.

The problem: after you scrape product specs from a bunch of sites, how do you decide
if a value is safe to publish? The catch is you never actually see the "true" spec.
`16000 MB` of RAM is a unit slip. `160 GB` of RAM is an impossible typo. `512 GB` of
storage can be perfectly real — just copied from the wrong variant. And "5 sites
agree" often just means 5 sites copied the same bad feed.

So instead of a classifier that outputs one label, I modelled each value as one of six
hidden "worlds" (correct / unit error / wrong product / typo / missing / garbled),
started from a prior based on how much I trust the source, updated it with Bayes as
cheap clues arrive, and then picked the action (accept / repair / buy more evidence /
flag to a human / reject) by *minimum expected cost* — because publishing a wrong spec
is ~20x more expensive than flagging one for a human.

Then I tested it on 40 labelled cases against a deliberately dumb "score + threshold"
baseline. Here's the humbling part:

→ Yes, my fancy version had the lowest average cost (2.30 vs 3.10, and it was
statistically significant).
→ But the median per-case difference was ZERO. Only 9 of 40 cases actually changed.
→ And all three versions committed the exact same 2 catastrophic mistakes.
→ The lower cost came almost entirely from punting 57% of cases to a human — not from
being smarter.

The most useful feedback came from strangers, not the model. Someone on a
web-scraping community pointed out my "cross-source agreement" signal was double-
counting copies of the same feed — which flipped one of my decisions from "repair" to
"flag." A statistician reminded me that priors set from experience are fine for an
internal pipeline but not for a research claim. And an ML practitioner gave me the
brutal test I used above: "build the dumb baseline and check if the smart layer
actually pays rent."

Biggest lesson: a probability of "97% correct" is worthless if it's only right 60% of
the time. Calibration isn't a footnote — an overconfident "looks fine" quietly
destroys the whole cost calculation.

Built with an AI assistant as a Socratic tutor (I owned every design call; it taught,
questioned, and drafted). Full write-up, code, and the review logs are in the comments.

What signals do you trust most for catching bad data *after* the scrape? Genuinely
curious how people handle the "everyone copied the same wrong value" problem.

#datascience #dataengineering #machinelearning #bayesian #ainative

---

## First comment (the link)

Repo + preprint (honest limitations and all): https://github.com/ChiragG2101/product-normalization-belief-engine

It's a Week-1 learning project, so it's deliberately a "way of thinking" more than a
production system — feedback and holes-poking very welcome.

---

## Posting notes
- Keep the body link-free; put the repo URL in the first comment right after posting.
- Best to post, then reply to early comments within the first hour (LinkedIn rewards
  early engagement).
- The closing question is the point — it invites the same kind of discussion that
  actually improved the model.
- If you want a shorter variant, cut the two middle paragraphs and keep: hook →
  the "median difference was zero" surprise → the calibration lesson → question.

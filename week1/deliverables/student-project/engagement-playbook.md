# Engagement Playbook — turning views into real discussions

Diagnosis (from actual results): posts are **visible and getting views**, but
views aren't converting to replies, on **old-but-inactive, low-karma/low-follower**
accounts. So we fix TWO things: (1) **reach** (cold accounts get throttled), and
(2) **conversion** (the post gives no compelling reason to reply). This is the
target — *not* virality. For this deliverable, 5–10 real back-and-forths beats
10k silent views (and virality bait attracts junk + spam flags).

---

## The 6 root causes of "views but no replies" (and the fix)

1. **The post is too complete.** A polished, finished write-up signals "nothing
   left to add." → Leave an obvious gap; ask ONE sharp question; take a mild
   stance people can push back on.
2. **Answering costs too much effort.** A 5-paragraph post with 3 questions gets
   0 replies; a 4-line post with 1 concrete question gets 10. → Cut length ~60%.
   One question, not three.
3. **No identity/credibility hook.** Cold account + no context = no trust. →
   Lead with a one-line credential ("SWE, new to Bayes") — relatable, invites
   "here's what I'd do."
4. **No reason to comment vs. upvote.** People upvote silently unless prompted. →
   End with a direct ask: "How do YOU handle X?" or a mild-wrong opinion that
   invites correction (people reply to correct far more than to agree).
5. **Died in the first hour.** Algorithms test-show to a few; no early activity →
   buried. → Be present the first 60–90 min; reply within minutes; seed 1
   follow-up comment yourself adding a detail.
6. **Reach cap from cold accounts.** Low karma/followers → tiny initial audience.
   → Warm up: comment valuably on others' threads for a few days FIRST; reply-guy
   into existing conversations (comments out-reach posts on cold accounts).

**The single biggest lever:** switch from *posting a project* to *asking one
opinionated question* + *being present for the first hour*.

---

## Platform 1 — Reddit

**How it works:** early upvote velocity + comments in the first ~1h decide reach.
Comments count more than upvotes for ranking discussions. Cold accounts see small
initial test audiences.

**Strategy:**
- **Warm up 2–3 days:** leave 5–10 genuinely useful comments on recent threads in
  r/dataengineering, r/WebScrapingInsider. Get to ~20–50 comment karma first.
- **Comment before you post.** On cold accounts, a *good comment* on a busy thread
  reaches more people than your own post. Do this deliberately — it's not a
  consolation prize, it's the higher-reach move, and it counts for Sec 5–7.
- **Post timing:** weekday mornings US Eastern (roughly 13:00–15:00 UTC) when
  r/dataengineering is busiest.
- **Format:** short. Title = the question. Body = 3–5 lines of context + ONE
  question. No links (removal trigger + looks salesy).
- **Title formula that works here:** "How do you handle X?" or "Is Y overkill vs.
  Z?" — practical, opinionated, answerable in one comment.
  - e.g. *"How do you handle cross-source agreement that isn't independent?"*
  - e.g. *"Per-field 'belief + expected cost' for data validation — overkill vs.
    rules + thresholds?"*
- **First hour:** reply to every comment within minutes; ask each replier a
  follow-up ("would that hold when sources share a parent company?").
- **Recover a dead post:** don't repost. Instead, take its core question into a
  *comment* on a busy existing thread, or the weekly "megathread" if the sub has one.

---

## Platform 2 — X / Twitter

**How it works:** the first 30 min of engagement (replies > likes) drives reach;
replies from others and your replies-to-replies compound. Cold accounts with few
followers have almost no organic reach — so **reply-first, not post-first.**

**Strategy (reply-guy strategy — most effective for small accounts):**
- **Reply into big accounts' threads** in your niche (data eng / ML / Bayesian
  folks) with a genuinely useful, specific take. This borrows their audience and
  is how small accounts grow. This is your PRIMARY X move, not original threads.
- **When you post original:** a thread, hook in tweet 1, NO link in tweet 1
  (links suppress reach — put any link in a reply).
- **Hook formulas (tweet 1) — must stop the scroll:**
  - Counterintuitive result: *"'160GB RAM' looks like an obvious typo. My model
    refuses to call it one. Here's why that's correct 🧵"*
  - Confession/relatable: *"Scraping data is easy. Deciding if a single value is
    TRUE is the part nobody warns you about. 🧵"*
  - Question hook: *"How do you decide whether to trust a scraped value you can't
    verify? Here's the model I landed on — tell me where it breaks 🧵"*
- **Post time:** weekday ~14:00–16:00 UTC or ~US-morning; be present 30–60 min.
- **Engagement mechanics:** end with a question; quote-tweet yourself a day later
  with the "one surprising thing"; reply to everyone.
- **Cadence for Sec 5–7 (~21–28 comments/7 days):** mostly *replies* on others'
  posts (5–6/day of substance), plus your one thread.

---

## Platform 3 — LinkedIn

**How it works:** rewards dwell-time + early comments; favors personal-story +
professional-insight framing; NO outbound links in the post body (put in comments).

**Strategy:**
- **Format:** hook line (1 sentence, punchy) → whitespace → short story/insight in
  1–2 line paragraphs → one question to the audience.
- **Hook lines that work:**
  - *"'Pick the most likely answer' is usually the wrong rule. Here's what changed
    how I think about data quality."*
  - *"I spent a week not writing code — and it made my data agent better."*
- **Put the preprint/GitHub link in the FIRST COMMENT, not the post** (link-in-post
  kills reach).
- **First hour:** reply to every comment; ask commenters a follow-up.
- **Tag sparingly:** 1–2 genuinely relevant people/communities, not a tag dump.
- **Hashtags:** 3–5 (#dataengineering #dataquality #machinelearning).

---

## Platform 4 — PyMC Discourse / Slack (the highest-value discussion venues)

These are NOT virality plays — they're where the *best* technical replies live,
and they reward specificity.
- **PyMC Discourse:** post the ONE priors/expected-loss question, show the actual
  numbers (your §3 board, §4 update), and end with a precise ask. Specific >
  broad here; maintainers answer real questions. Reply fast, iterate in-thread.
- **Data Quality Camp / dbt / MLOps Slack:** post in the right channel
  (#data-quality etc.), keep it conversational, ask the correlated-sources
  question. Slack rewards being present and replying in-thread.
- These count strongly for Sec 5–7 and produce the best "design change from a
  discussion" material.

---

## The reusable "conversion" template (any platform)

```
[1-line credential]  — "SWE, newer to Bayesian methods."
[2–4 lines context]  — the problem + your approach, minimal.
[1 mild-wrong or opinionated stance]  — gives people something to correct.
[ONE concrete question]  — answerable in a single reply.
[no link in the body]
```
Then: **be present the first hour, reply to everyone, ask each a follow-up.**

---

## What NOT to do (kills engagement / risks bans)
- Don't post the same text to many places at once.
- Don't put links in the initial post/tweet.
- Don't ask 3+ questions — dilutes replies.
- Don't post and leave.
- Don't buy engagement or use pods — attracts junk + flags.
- Don't chase raw virality — it attracts low-quality replies and misses the point
  (real discussion) of Sections 5–7.

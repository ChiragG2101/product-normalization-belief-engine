"""Domain constants for the Product Data Normalization belief engine.

Every number here is transcribed directly from
`decisions/belief-engine-decision-model.md` (sections 3, 4, 5). If code and the
markdown model disagree, the markdown is the design and this file has the bug.
"""

from __future__ import annotations

# The six MECE hidden worlds (section 1). Order is fixed and reused everywhere.
WORLDS = [
    "correct",
    "unit_error",
    "wrong_product",
    "typo",
    "missing",
    "garbled",
]

# Section 3.1 -- source-reliability priors, as token counts out of 100.
# Keys are the three source tiers; values are P(world) x 100 for that source.
PRIORS = {
    "MFR": {  # manufacturer / high trust
        "correct": 80,
        "unit_error": 4,
        "wrong_product": 6,
        "typo": 3,
        "missing": 4,
        "garbled": 3,
    },
    "MID": {  # mid-reliability retail (the section 4 worked case uses this)
        "correct": 50,
        "unit_error": 10,
        "wrong_product": 15,
        "typo": 5,
        "missing": 10,
        "garbled": 10,
    },
    "SKY": {  # sketchy aggregator / low trust
        "correct": 30,
        "unit_error": 12,
        "wrong_product": 20,
        "typo": 8,
        "missing": 15,
        "garbled": 15,
    },
}

# Section 4.2 -- likelihood P(evidence | world) for each evidence signal the agent
# can read. Each inner dict is P(signal fires | world); values are independent
# 0..1 probabilities, NOT a budget (they need not sum to 1).
#
# Signals modelled:
#   "oos"        - value reads out-of-support / implausible range
#   "unit"       - value becomes plausible only after a unit conversion
#   "xsource_agree" - other sources agree with this value
#   "xsource_disagree" - other sources disagree with this value
#   "empty"      - value is empty / null / placeholder-empty
#   "junk"       - value is present but unparseable as this field
LIKELIHOODS = {
    # section 4.2 exactly (P(out-of-support | world))
    "oos": {
        "correct": 0.02,
        "unit_error": 0.40,
        "wrong_product": 0.10,
        "typo": 0.90,
        "missing": 0.01,
        "garbled": 0.01,
    },
    # a clean unit-convertible footprint (e.g. 16000 MB -> 16 GB)
    "unit": {
        "correct": 0.02,
        "unit_error": 0.85,
        "wrong_product": 0.05,
        "typo": 0.10,
        "missing": 0.01,
        "garbled": 0.02,
    },
    # cross-source agreement. NOTE: down-weighted for correlation (policy 1.1,
    # from the r/WebScrapingInsider discussion -- agreement is not independence). These
    # are the discounted strengths.
    "xsource_agree": {
        "correct": 0.60,
        "unit_error": 0.15,
        "wrong_product": 0.30,
        "typo": 0.10,
        "missing": 0.02,
        "garbled": 0.02,
    },
    "xsource_disagree": {
        "correct": 0.10,
        "unit_error": 0.30,
        "wrong_product": 0.60,
        "typo": 0.40,
        "missing": 0.05,
        "garbled": 0.05,
    },
    "empty": {
        "correct": 0.001,
        "unit_error": 0.001,
        "wrong_product": 0.001,
        "typo": 0.001,
        "missing": 0.99,
        "garbled": 0.02,
    },
    "junk": {
        "correct": 0.001,
        "unit_error": 0.001,
        "wrong_product": 0.001,
        "typo": 0.01,
        "missing": 0.02,
        "garbled": 0.97,
    },
}

# The terminal + information actions (section 5.2).
ACTIONS = ["ACCEPT", "REPAIR", "BUY", "FLAG", "REJECT"]
TERMINAL_ACTIONS = ["ACCEPT", "REPAIR", "REJECT"]  # policy B is restricted to these

# Section 5.4 -- the cost matrix. cost[action][true_world].
COST = {
    "ACCEPT": {
        "correct": 0, "unit_error": 20, "wrong_product": 20,
        "typo": 20, "missing": 20, "garbled": 20,
    },
    "REPAIR": {
        "correct": 18, "unit_error": 0, "wrong_product": 8,
        "typo": 4, "missing": 12, "garbled": 12,
    },
    "BUY": {
        "correct": 1, "unit_error": 1, "wrong_product": 1,
        "typo": 1, "missing": 1, "garbled": 1,
    },
    "FLAG": {
        "correct": 2, "unit_error": 2, "wrong_product": 2,
        "typo": 2, "missing": 2, "garbled": 2,
    },
    "REJECT": {
        "correct": 5, "unit_error": 6, "wrong_product": 6,
        "typo": 2, "missing": 1, "garbled": 1,
    },
}

# Section 6.2 -- derived ACCEPT threshold (operating value, conservative).
ACCEPT_THRESHOLD = 0.95
# Section 6.3 -- hard cap on information buys before forced FLAG.
MAX_BUYS = 2

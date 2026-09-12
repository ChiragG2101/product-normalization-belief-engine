# Results -- belief engine vs. autonomous vs. baseline

Cases: 40

| policy | avg cost | human-review rate | wrong publishes (cost 20) | accept precision | accept recall |
|--------|:---:|:---:|:---:|:---:|:---:|
| full | 2.3 | 0.575 | 2 | 0.75 | 0.333 |
| autonomous | 3.075 | 0.0 | 2 | 0.818 | 0.5 |
| baseline | 3.1 | 0.325 | 2 | 0.75 | 0.333 |

**Belief-vs-baseline agreement:** 0.625 -> belief layer changes decisions vs. baseline (but see significance test)

## Is the cost gap statistically significant? (paired Wilcoxon signed-rank)

| comparison | median cost diff | mean cost diff | W | z | p (two-sided) | significant @0.05 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| full vs baseline | 0.0 | -0.8 | 1.5 | -2.429 | 0.0152 | True |
| full vs autonomous | 0.0 | -0.775 | 17.5 | -2.94 | 0.0033 | True |

_Paired Wilcoxon signed-rank on per-case cost differences. If p >= 0.05 the average-cost gap is NOT statistically significant at N=40 -- the lower mean cost is a point estimate, not a proven win (and note it is largely bought by a higher FLAG/escalation rate)._

## Calibration -- full
| P(correct) bin | n | mean predicted | empirical correct |
|---|:---:|:---:|:---:|
| 0.00-0.50 | 23 | 0.088 | 0.13 |
| 0.50-0.70 | 3 | 0.637 | 1.0 |
| 0.70-0.90 | 6 | 0.804 | 1.0 |
| 0.90-0.95 | 3 | 0.935 | 1.0 |
| 0.95-1.01 | 5 | 0.978 | 0.6 |

## Calibration -- autonomous
| P(correct) bin | n | mean predicted | empirical correct |
|---|:---:|:---:|:---:|
| 0.00-0.50 | 21 | 0.098 | 0.095 |
| 0.50-0.70 | 8 | 0.61 | 0.875 |
| 0.70-0.90 | 3 | 0.813 | 1.0 |
| 0.90-0.95 | 8 | 0.944 | 0.75 |
| 0.95-1.01 | 0 | None | None |

## Calibration -- baseline
| P(correct) bin | n | mean predicted | empirical correct |
|---|:---:|:---:|:---:|
| 0.00-0.50 | 21 | 0.098 | 0.095 |
| 0.50-0.70 | 8 | 0.61 | 0.875 |
| 0.70-0.90 | 3 | 0.813 | 1.0 |
| 0.90-0.95 | 8 | 0.944 | 0.75 |
| 0.95-1.01 | 0 | None | None |

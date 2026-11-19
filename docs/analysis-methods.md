# Analysis methods

How the derived numbers are defined. Everything here is computed at publish time.

## MR bands
| Band | Rule |
|---|---|
| **Diamond and below** | Not yet Master (Rookie through Diamond). Ranked by league, no MR. One band, labelled by league name only (e.g. "Platinum") where a league is shown. |
| **MR 1200-1400** | Master, effective MR < 1400 (includes anything under 1200). |
| **MR 1400-1600** | 1400 ≤ effective MR < 1600 |
| **MR 1600-1800** | 1600 ≤ effective MR < 1800 *(added: the brief skipped this range, see open questions)* |
| **MR 1800-2000** | 1800 ≤ effective MR < 2000 |
| **MR 2000+** | effective MR ≥ 2000 |
| **MR unknown** | Master with no MR recorded (e.g. older opponents, local matches). Shown in lists, left out of band statistics. |

- A player's band is taken **per set**, from their MR at that set, not their current MR. A player who climbs counts in each band they played in.
- Local and casual matches (no rank data) are MR unknown unless the reviewer enters a rank.

### Japan MR adjustment
Japanese MR is inflated relative to other regions. For banding and weighting:

`effective_mr = mr - 200` when `players.region = 'JP'`, else `effective_mr = mr`.

So a Japanese 2300 MR player is treated like a 2100 from another region. This is an approximation, and the page says so wherever effective MR is used. The raw MR is always shown next to it. If region is unknown, no adjustment is made.

## Weighting toward stronger players
Used **only in data processing**: the "what winning players do" traits, the archetype-matchup model, and the observations evidence. The interface shows the results, not the weights.

| Effective MR | Meaning | Weight |
|---|---|---|
| Diamond and below | developing | 0.5 |
| < 1600 | solid Master | 0.75 |
| 1600-1800 | strong | 1.0 |
| 1800-2000 | excellent player | 2.0 |
| 2000-2100 | true master of the game | 3.0 |
| 2100+ | top players, regional-level threats | 4.0 |
| MR unknown | | 0.75 (or excluded, configurable) |

Weights live in `snapshot_meta` so each snapshot records the weights it used. A trait's "weighted win rate" is Σ(weight × won) / Σ(weight) over player-sets.

## Archetype deviation
Per player, across their sets:
- **Modal archetype**: the most common read (ties broken by most recent).
- **Deviation rate**: share of sets with a different archetype read. Only Medium or High confidence reads count; Low-confidence reads are shown but not counted.
- **Deviation direction**: which archetype they move to, and in what context. Context is split by:
  - result (win / loss);
  - the opponent's archetype;
  - character;
  - being behind (lost game 1, or down in games) vs ahead.
- **Archetype by result**: archetype mix and spectra means in **won sets vs lost sets**, with the difference highlighted when it's larger than the spread between sets.
- **Elasticity in practice**: combine the Adaptability spectrum with deviation. A player who deviates mostly *after losing game 1* is adjusting. One who deviates at random is unstable.

## Spectra over sets
- A player's score per axis = the rounded mean of per-set scores, with the range and number of sets shown.
- Per-set scores are percentile strata against every player-set reviewed so far (20/40/60/80th percentile cut points), so they shift slightly as data grows. Each snapshot recomputes them and records the cut points.

## Sample size and confidence
Every derived number carries `n`. Display rules:
- n < 3 sets: shown greyed, labelled "early read".
- 3-9: Medium.
- 10+: High (if the reads agree).
- Band and matchup cells with fewer than 5 player-sets show the count instead of a rate.

## Predictions
- Each set's pre-review prediction is shown with its grade (winner and score right or wrong, what it missed).
- Accuracy over time: a running hit rate by month and by review level, so it's visible whether predictions improve.

## Archetype-vs-archetype predictions
Two sources, shown side by side:
1. **Observed:** set results when archetype A met archetype B (MR-weighted, with n).
2. **Model:** a prior from the skills' guidance (e.g. a patient Defensive player is favoured against an Aggressive player who burns out; Fundamentalist players struggle against heavy use of system mechanics), adjusted by the MR difference. The spectra pairings work the same way (e.g. Impulsive defense vs a frame-trap-heavy offense).

Where the two disagree with enough data, the observed result wins, and the disagreement becomes an observation.

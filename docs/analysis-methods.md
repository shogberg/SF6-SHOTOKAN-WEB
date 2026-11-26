# Analysis methods

How the derived numbers are defined. Everything here is computed at publish time.

## MR bands
| Band | Rule |
|---|---|
| **Under Master** | Not yet Master (Rookie through Diamond). Ranked by league, no MR. One band (id `diamond_below`, labelled "Diamond and below" until 2026-11-26), labelled by league name only (e.g. "Platinum") where a league is shown. |
| **Below 1400** | Master, effective MR < 1400. |
| **1400-1599** | 1400 ≤ effective MR < 1600 |
| **1600-1699** | 1600 ≤ effective MR < 1700 *(split from 1600-1800 on 2026-11-26)* |
| **1700-1799** | 1700 ≤ effective MR < 1800 |
| **1800-1999** | 1800 ≤ effective MR < 2000 |
| **2000+** | effective MR ≥ 2000 |
| **MR unknown** | Master with no MR recorded (e.g. older opponents, local matches). Shown in lists, left out of band statistics. |

- A player's band is taken **per set**, from their MR at that set, not their current MR. A player who climbs counts in each band they played in.
- Local and casual matches (no rank data) are MR unknown unless the reviewer enters a rank.

### Japan MR adjustment
**Status: deferred.** No Japanese data is being imported for now, and players' region isn't recorded yet (it may be possible to read it from replays later). Until then every player is treated as non-JP. The rule below is kept so it's ready when JP data arrives.

Japanese MR is inflated relative to other regions. For banding and weighting:

`effective_mr = mr - 200` when `players.region = 'JP'`, else `effective_mr = mr`.

So a Japanese 2300 MR player is treated like a 2100 from another region. This is an approximation, and the page says so wherever effective MR is used. The raw MR is always shown next to it. If region is unknown, no adjustment is made.

## Weighting toward stronger players
> **Status: draft weights, pending review.** The values below are a starting point and will change.
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
- **Deviation rate**: share of sets with a different archetype read. All reads count (Quick reviews are mostly Low confidence, so excluding them would leave too little); each set's read confidence is shown next to it.
- **Deviation direction**: which archetype they move to, and in what context. Context is split by:
  - result (win / loss);
  - the opponent's archetype;
  - character;
  - being behind (lost game 1, or down in games) vs ahead.
- **Archetype by result**: archetype mix and spectra means in **won sets vs lost sets**, with the difference highlighted when it's larger than the spread between sets.
- **Elasticity in practice**: combine the Adaptability spectrum with deviation. A player who deviates mostly *after losing game 1* is adjusting. One who deviates at random is unstable.

## Spectra over sets
- A player's score per axis = the rounded mean of per-set scores, with the range and number of sets shown.
- Per-set scores are percentile strata (20/40/60/80th percentile cut points) against every reviewed player-set **except the configured player's** (settings `me`), so the coached player is compared with everyone else instead of a pool that is largely their own games. Each other player counts equally: their sets share one weight, min(1, games / 10), so players with only a couple of short sets count less. The tools recalibrate them (`spectra_calibrate.py`) and store them in sf6.db (settings `spectra_cuts`); since 24 Nov 2026 the pool is 234 player-sets from 122 players (effective weight 47).
- **Personal baseline:** for the configured player only, each set is also compared with the median of their own sets in the previous 7 days (`player_baseline` table): the eight spectra (raw values, and the change on the 1-5 scale) and per-game stats (counter hits, throws, Drive Rush, decision presses, damage per decision press, wake-up and after-block choices). The set page shows it as "vs their last 7 days".

## Traits views
- **All sets:** winner vs loser of every decided set (paired within the set).
- **Everyone else:** the same, leaving out sets with the configured player.
- **You: wins vs losses:** the configured player's own stats in the sets they won against the sets they lost. Not paired (different opponents and days), so each side is the MR-weighted mean over its sets and there is no "higher in" share.

## Damage
- A hit's damage is the permanent life the victim lost: the drop in the recoverable-health cap over the combo. When a hit lands while the victim has white (recoverable) health, the white health it cashes in counts. Damage that only adds white health (a blocked Arjun string, a Drive Reversal) counts 0 until a later hit cashes it in.
- Every set with a capture was re-scored this way on 23 Nov 2026 (`tools/rescore_damage.py`); 11 video-only games keep the older count.

## Sample size and confidence
Every derived number carries `n`. Display rules:
- n < 3 sets: shown greyed, labelled "early read".
- 3-9: Medium.
- 10+: High (if the reads agree).
- Band and matchup cells with fewer than 5 player-sets show the count instead of a rate.

## Predictions
- Each set's pre-review prediction is shown with its grade (winner and score right or wrong, what it missed).
- Accuracy over time: a running hit rate by month and by review level, so it's visible whether predictions improve.
- Compare against a baseline: picking the higher-MR player. As of 23 Nov 2026, blind predictions picked the winner in 72% of 92 sets and the higher-MR player won 76% of the 83 sets where both MRs were known, so the pick alone doesn't beat MR yet.

## Archetype-vs-archetype predictions
Two sources, shown side by side:
1. **Observed:** set results when archetype A met archetype B (MR-weighted, with n).
2. **Model:** a prior from the skills' guidance (e.g. a patient Defensive player is favoured against an Aggressive player who burns out; Fundamentalist players struggle against heavy use of system mechanics), adjusted by the MR difference. The spectra pairings work the same way (e.g. Impulsive defense vs a frame-trap-heavy offense).

Where the two disagree with enough data, the observed result wins, and the disagreement becomes an observation.

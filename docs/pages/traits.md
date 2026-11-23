# What winning players do (`/analysis/traits`)

**Built (2026-11-22), first version:** the winner and loser of each set compared stat by stat (per-game counts, defensive rates, damage taken by situation, spectra), each set weighted by its players' MR weight, with "winner higher in X% of sets" (ties left out) and the archetype win rates. A "What stands out" list shows stats where the winner was higher or lower in at least 62% of 20+ sets. API: `GET /api/v1/analysis/traits` (`api/app/queries/traits.py`). The plan below is the full version.

An overview of the archetypes and spectra that go with winning, **weighted toward higher-MR players** (weights in [analysis-methods.md](../analysis-methods.md); the page explains the weighting in one line but doesn't expose it as a control).
- **Archetypes:** weighted set win rate per archetype and lean, with n; how often each archetype appears in each band.
- **Spectra:** for each axis, weighted win rate by score (1-5) and the score range most common among 1800+ players.
- **Combinations:** the most and least successful spectrum combinations with enough data (e.g. Elastic + Steady).
- **Profile of a consistent winner:** a written summary (from the SF6-SHOTOKAN agent description), with the current numbers next to each claim so it can be checked.

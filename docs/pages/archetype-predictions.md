# Archetypes (`/analysis/archetypes`)

Renamed from "Archetype matchups" on 2026-11-26; `/analysis/archetype-predictions` redirects here.

## Built (2026-11-26)
- **The four archetypes:** hand-written notes on what each archetype looks like and why players lean that way (character kit, matchup, score, MR), plus general notes. Text in `web/src/lib/archetypeNotes.ts`, dated; rewrite when the tables stop matching it. Rewritten 2026-11-27 after the generated reads were recalibrated against the pool (four reads instead of mostly Aggressive / Balanced; obs-0038).
- **Sets filter:** Ranked (default), Other or All. **MR filter:** All plus the Stats by MR bands; the band of the player whose archetype it is.
- **Summary per archetype:** share of reads, player-sets, players, set win rate, most common characters and leans.
- **Head to head:** set win rate of the row archetype against the column archetype (the filter applies to the row player).
- **Spectra by archetype:** mean of each spectrum.

API: `GET /api/v1/analysis/archetypes?band=` returns `summary` (per archetype), `matrix` and `player_sets`, plus `bands`.

## Still planned: predictions

Predictions for the most common archetypes and spectra when they meet.
- **Archetype matrix:** rows and columns are Aggressive, Defensive, Fundamentalist and Balanced (and common leans). Each cell shows:
  - the model's predicted edge and why (one line, from the skills' guidance);
  - the observed MR-weighted win rate with n;
  - a flag when the two disagree.
- **Spectrum pairings:** selected axis-vs-axis pairs where one trait directly answers another, e.g.:
  - Impulsive defense vs Mindful offense (frame traps);
  - Spendthrift vs Conservative (burnouts);
  - Inelastic vs Elastic (adapting across games);
  - Proactive vs Reactive (walk-ins vs whiff punishes).
- **Most common matchups first:** sorted by how often the pairing actually occurs, so the top of the page covers what players face most.
- **Accuracy:** how often the model's matrix call matched real set results, over time.

# Stats by MR (`/analysis/mr-bands`)

How players differ by MR band. Named "MR bands" until 2026-11-26. Bands are defined in [analysis-methods.md](../analysis-methods.md): Under Master, Below 1400, 1400-1599, 1600-1699, 1700-1799, 1800-1999, 2000+. MR unknown player-sets are left out and counted.

**Unit:** a player-set (one player in one reviewed set), banded by their MR at that set. A cell is the band's mean over its player-sets; hovering shows the median and n. Bands under 15 player-sets are dimmed.

## Sections (built 2026-11-26)
- **What changes with MR:** hand-written notes on button economy, Drive economy, offense / pressure / oki, defense, spectra and archetypes. They're dated and come with the sample size; text in `web/src/lib/mrBandsNotes.ts`. Rewrite a note when the live tables stop matching it.
- **Biggest differences between neighbouring bands:** every measure and spectrum, change between adjacent bands (both with 15+ player-sets) in units of the measure's spread across all player-sets, top 12.
- **By band:** player-sets and players per band.
- **Tables (bands as columns):**
  - Button economy: decision presses per round, damage per decision press, share of the set's decision presses, damage dealt per round.
  - Drive economy: raw / pressure / combo Drive Rushes, Drive Reversals and burnouts per game; Drive spent, OD, lost blocking and gained on block per round; super spent per round; lost rounds ending with 3 super bars. The round's loser is taken as the player who took its last hit, so time-outs can miss.
  - Offense, pressure and oki: throws, counter hits and punish counters per game; share of damage dealt in neutral, pressure, oki and punishes.
  - Defense: anti-airs, throw techs and perfect parries per game; hold-block and press rates after blocking and on wake-up; close punish windows punished; jump-ins anti-aired and stopped when the player was free to anti-air (%), and jump-ins that hit or were blocked while free, per game (since 2026-11-27); damage taken per round.
  - Neutral (since 2026-11-27): whiff-punish chances taken (%) and own whiffs punished per game.
- **Damage taken by lens:** share of damage taken by how it was taken. The analyzer only computes lenses for the reviewed (focus) player, so these come from fewer player-sets.
- **Spectra (1-5)** and **archetype mix** (share and set win rate per archetype) per band.
- A toggle leaves out the site owner (settings `me`), whose sets are most of the data.
- **Sets filter** (added 2026-11-26): Ranked (default), Other (casual, custom room, local, tournament, unknown) or All, on `player_set.context`. Custom room and casual sets are often training and can be lopsided, so the notes are written from ranked sets.

API: `GET /api/v1/analysis/mr-bands?view=all|others&context=ranked|other|all` (API default `all`; the page asks for `ranked`) returns `bands` (with player-set and player counts), `unknown_left_out`, `small`, `metrics`, `lenses`, `spectra` (each row: `key`, `label`, `group`, `bands` → `{mean, median, n}`), `archetypes` per band and `biggest_differences`.

Still to do: quartiles, a two-band compare view, MR weighting inside a band, and the Japan adjustment once region data exists.

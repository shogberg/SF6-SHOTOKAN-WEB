# Data model

The site reads a **snapshot** database built from the local `sf6.db`. It has two layers:

1. **Source tables**, copied from `sf6.db` as they are (minus anything private).
2. **Derived tables**, computed at publish time for the views. The API mostly reads these.

## 1. Source tables (from sf6.db)

| Table | One row per | Key columns used by the site |
|---|---|---|
| `players` | player | `player_id`, `cfn_id`, `name`, `first_seen`, `last_seen` |
| `player_names` | name a player has used | for search and renamed players |
| `sets` | set | `set_key`, `played_date`, `ranked`, `format`, `review` (Quick / Full / Tournament), `focus_player_id`, `opp_player_id`, characters, games won, `winner_player_id`, `focus_mr_start`, `note` |
| `games` | game (replay) | `replay_id`, `set_key`, `game_no`, players and characters, control type, `p1_mr` / `p2_mr`, `p1_lp` / `p2_lp`, `p1_rank` / `p2_rank`, winner, round score |
| `hits` | damaging hit or combo | attacker, victim, damage, starter, hit kind, anti-air, situation, lens, Drive and super spent, knockdown |
| `events` | burnout, perfect parry | |
| `resources` | player per round | Drive and super spending, gains and losses |
| `parries` | Drive Parry | cost, regained, what happened next |
| `timings` | after-block and wake-up action | used for temperament |
| `set_stats` | player per set per metric | per-set counters (throws, techs, counter hits, after-block attacks, damage-taken shares…) |
| `reads` | player per set | archetype, lean, confidence, evidence, counter note |
| `spectra` | player per set per axis | score 1-5, label, evidence |
| `habits` | habit | kind (Strength / Leak / Pattern), area, seen, times, fix |
| `usage` | move per player per game | move counts |
| `review_docs` | set and dataset | JSON for Full and Tournament reviews: story, gameplan, prediction, fixes, training, tournament audit |

Excluded from the snapshot: local file paths (`games.capture_file`), dashboard links, and anything you mark private.

## 2. New fields needed upstream (in SF6-SHOTOKAN)

| Field | Where | Why |
|---|---|---|
| `players.region` (e.g. JP, NA, EU, ASIA, other) | players | Japan MR adjustment. Not in the capture data; entered by hand or from CFN when known. Default: unknown, treated as non-JP. |
| `players.alias_public` | players | Optional stable alias if a public snapshot is ever made. |
| Opponent MR / league per set | `games.p*_mr`, `p*_rank` | Capture v3.3 saves both players' MR and LP from the replay info. Older sets only have the focus player's MR (`sets.focus_mr_start`); those opponents stay **MR unknown** and are left out of band stats. |
| `sets.event` / `sets.context` | sets | Ranked, casual, local, tournament. `ranked` and `note` cover this loosely today; a clean enum makes filters reliable. |
| `predictions` as a table | new | Today predictions live in `review_docs` (dataset `prediction`). A proper table (set, player, predicted winner/score/archetype, confidence, written_at, graded outcome) makes accuracy tracking easy. |
| `observations` | new | Dated notes for the Observations page (see below). |

## 3. Derived tables (built at publish)

### Player
- **`player_profile`**: one row per player.
  - Modal archetype, lean and confidence.
  - Spectra means and spread per axis.
  - Record in sets and games, characters played.
  - Per-game rates (throws, techs, anti-airs, counter hits, raw Drive Rushes, burnouts, after-block and wake-up attack %).
  - Top strengths and leaks (as `profiles_from_db.py` builds them today).
  - MR band at their latest set.
- **`player_archetype_history`**: one row per player per set.
  - The archetype read, result, MR band, opponent's archetype, character.
  - Whether it's a **deviation** from their modal archetype.
- **`player_archetype_summary`**: one row per player per archetype.
  - Sets, wins and losses, win rate.
  - Spectra means **in wins vs losses**.
  - Most common deviation direction (e.g. "Balanced → Aggressive when behind").

### Sets
- **`set_summary`**: one row per set.
  - Everything the set list needs in one row: players, characters, MR / league at the time, result, game scores, review level.
  - Prediction headline and its grade.
  - Archetype of each side.

### Head to head
- **`h2h_summary`**: one row per ordered pair of players.
  - Sets and record, first and last meeting.
  - Each side's archetype in this pairing vs overall.
  - Biggest stat deltas (e.g. "jon presses after blocking 10.7× a game vs shog, 4.8× in general").

### Analysis
- **`mr_band_stats`**: one row per band per metric.
  - Mean, median, p25 / p75 and n players for: per-game rates, spectra, archetype mix, Drive economy, damage-taken lenses.
- **`trait_success`**: one row per spectrum axis per score (and per archetype).
  - Set win rate, **MR-weighted** win rate, n.
  - Mean MR of players at that score.
- **`archetype_matchups`**: one row per (archetype A, archetype B), and per (axis A score, axis B score) for selected axis pairs.
  - Observed sets, A's win rate, MR-adjusted expectation.
  - Model prediction with its basis, confidence.
- **`matchup_char`** *(phase 4, placeholder)*: one row per character pair.
  - Games, win rate, damage-taken lenses, common starters, punish rates.

### Meta
- **`snapshot_meta`**: `snapshot_id`, `built_at`, tool versions (analyzer, spectra, profile builder), band definitions, weights.
- **`observations`**: `obs_id`, `written_at`, `topic` (winning / struggling / model change / other), `title`, `body` (markdown), `evidence` (links to sets or players), `supersedes` (an earlier observation it revises).

## Keys and identity
- Players are keyed by `player_id` (local) and, when known, `cfn_id`. Local matches (no CFN) use the name given at review time. A later merge tool can link a local name to a CFN ID.
- Set keys are the joined replay IDs, as today (`JSHO2G1_JSHO2G2_JSHO2G3` for local captures).
- Characters use the game's character IDs plus display names from `char_names.json`.

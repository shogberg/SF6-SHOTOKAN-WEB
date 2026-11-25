# Player profile (`/players/{id}`)

**Header:** name (and past names), CFN ID if known, main characters, current MR / league (raw MR, plus effective MR if JP), record in sets and games, date range, number of reviewed sets by level.

## Sections
1. **Summary.** A short generated paragraph (as `profiles_from_db.py` writes today), plus confidence and sample size.
2. **MR over time** (built 2026-11-25). A line per character (MR is per character) from the player's reviewed ranked games: the MR before the first game, then the MR after each game. API: `GET /api/v1/players/{id}/mr?date_from=&date_to=&character=` returns the points (`at`, `character`, `mr`, `change`, `mr_after`, `source`, opponent and their MR, won) in played order, plus `characters` (first-played order, which fixes each line's colour) and `phases`.
   - A game's change is the tools' `games.p1/p2_mr_change`: observed from the same player's MR in the set's next game, or calculated for a set's last game with sfbuff's formula (Elo, K = 16: `round(16 * (result - 1 / (1 + 10^((opp - me) / 400))))`). Older snapshots without those columns use the formula for every game.
   - Controls in one row above the chart: presets Last day, Last week, Last month, Last phase, 90 days, Year, All; a From / To date range; a character picker when there's more than one. Hover shows a crosshair with each line's MR, change and opponent; a Table view lists every game.
   - **Last phase** starts at the latest ranked phase start in the publish config's `phases` (`[{"name": "...", "start": "YYYY-MM-DD"}]`, copied to `snapshot_meta.phases`). Buckler's battle log and ranking pages don't say which phase is current (checked 2026-11-25), so the dates are entered by hand; without them the button is disabled.
   - Only reviewed sets are in the database, so unreviewed matches between them show as a jump from one point to the next.
3. **Archetype.**
   - Modal archetype and lean, with confidence.
   - **Archetype by result:** archetype mix and spectra means in won sets vs lost sets, side by side. Differences bigger than normal set-to-set spread are highlighted, e.g. "In losses: Composure 4 (tilts) vs 2 in wins".
   - **Deviation:** how often they leave their usual archetype (rate, n), and where they go. A small transition list shows from → to, count, and context (after losing game 1 / vs Aggressive opponents / on character X).
   - **Timeline:** archetype per set over time, coloured by result.
4. **Spectra.** Eight spectrum bars (mean score, range across sets), each with its evidence line and a sparkline of per-set scores.
5. **Strengths and weaknesses.** Top Strength and Leak habits (count and number of sets), plus "what opponents did to them" (counter hits taken, anti-airs taken, throws taken vs teched).
6. **Per game.** Throws, techs, anti-airs, counter hits, punish counters, raw Drive Rushes, burnouts, after-block and wake-up attack %, compared with their MR band's median.
7. **Drive economy.** Spent / lost / gained per round vs band median.
8. **How to beat them.** Generated from extreme spectra plus review counter notes. For the site owner's own profile, this reads "How opponents beat you".
9. **Links:** all sets, head to head with frequent opponents, their band on the MR bands page.

API: `GET /players/{id}` (profile), `GET /players/{id}/archetypes` (history, by result, deviations).

## By character (schema 1.2)
When a player has played more than one character, the overview shows a **By character** table (sets and games won-lost, throws, anti-airs, counter hits, punish counters, burnouts and wake-up attacks per game on each character) and a **Character** picker that switches the Spectra and Per game sections to that character. Data: `player_character`, built from the source's `game_stats` (per game, with that game's character), so a mid-set character switch is split correctly. Sets reviewed before `game_stats` existed fall back to their whole-set stats (`stats_source = 'sets'`). Spectra are per set, so they count under the set's character.

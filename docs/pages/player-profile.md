# Player profile (`/players/{id}`)

**Header:** name (and past names), CFN ID if known, main characters, current MR / league (raw MR, plus effective MR if JP), record in sets and games, date range, number of reviewed sets by level.

## Sections
1. **Summary.** A short generated paragraph (as `profiles_from_db.py` writes today), plus confidence and sample size.
2. **Archetype.**
   - Modal archetype and lean, with confidence.
   - **Archetype by result:** archetype mix and spectra means in won sets vs lost sets, side by side. Differences bigger than normal set-to-set spread are highlighted, e.g. "In losses: Composure 4 (tilts) vs 2 in wins".
   - **Deviation:** how often they leave their usual archetype (rate, n), and where they go. A small transition list shows from → to, count, and context (after losing game 1 / vs Aggressive opponents / on character X).
   - **Timeline:** archetype per set over time, coloured by result.
3. **Spectra.** Eight spectrum bars (mean score, range across sets), each with its evidence line and a sparkline of per-set scores.
4. **Strengths and weaknesses.** Top Strength and Leak habits (count and number of sets), plus "what opponents did to them" (counter hits taken, anti-airs taken, throws taken vs teched).
5. **Per game.** Throws, techs, anti-airs, counter hits, punish counters, raw Drive Rushes, burnouts, after-block and wake-up attack %, compared with their MR band's median.
6. **Drive economy.** Spent / lost / gained per round vs band median.
7. **How to beat them.** Generated from extreme spectra plus review counter notes. For the site owner's own profile, this reads "How opponents beat you".
8. **Links:** all sets, head to head with frequent opponents, their band on the MR bands page.

API: `GET /players/{id}` (profile), `GET /players/{id}/archetypes` (history, by result, deviations).

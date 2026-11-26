# Stats by Character (`/matchups`)

Named "Characters" until 2026-11-26. **Built 2026-11-26:** character vs character game win rates.
- Every decided game counts from both sides (A's character vs B's, and B's vs A's). Mirror matches count as games, but have no win rate.
- **MR filter:** All plus the Stats by MR bands. A band keeps the games where the player using the character was in that band at the set, whatever the opponent's MR.
- The left table lists every character (games, W-L outside mirrors, win %, a bar against 50%). Picking one shows its win rate against each opponent character. Rows under 5 games are dimmed.
- **Sets filter:** Ranked (default), Other (casual, custom room, local, tournament, unknown) or All. Training sets can be lopsided: Cammy wins 78% of her non-ranked games.
- Most reviewed games include the site owner's Cammy, so Cammy's rows lean on one player.

API: `GET /api/v1/matchups?band=&context=ranked|other|all` (API default `all`) returns per character `games`, `games_non_mirror`, `won`, `lost`, `win_pct` and `vs` (per opponent character, `mirror` flagged), plus `bands` (filter values, "all" first).

Still planned (phase 4): the per-pairing detail at `/matchups/{a}/{b}`, with damage-taken lenses each way, common starters and punishes, anti-air and Drive Rush check rates, round-start range habits, and links to the sets and `matchup_notes`.

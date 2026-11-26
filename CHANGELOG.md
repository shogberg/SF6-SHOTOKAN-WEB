# Changelog

Notable changes to SHOTOKAN Web, newest first. Every push adds its changes here.

## 2026-11-26 (Stats by MR, Stats by Character, Archetypes, reviewed date)
- **Stats by MR** (was "MR bands", phase 3 first version):
    - Band tables for button economy, Drive economy, offense / pressure / oki, defense, damage taken by lens, spectra and archetype mix.
    - Biggest differences between neighbouring bands.
    - Dated hand-written notes (`web/src/lib/mrBandsNotes.ts`).
    - A "without the site owner" toggle.
    - New `GET /api/v1/analysis/mr-bands`.
- **Bands revised:** Under Master, Below 1400, 1400-1599, 1600-1699, 1700-1799, 1800-1999, 2000+ (`publish/common.py`). 1600-1800 is split in two, and "Diamond and below" is relabelled "Under Master" (id unchanged).
- **Stats by Character** (was the "Characters" placeholder): character vs character game win rates with an MR band filter. `GET /api/v1/matchups?band=`; the per-pairing detail is still planned.
- **Archetypes** (was "Archetype matchups"):
    - Notes on each archetype and why players lean that way (`web/src/lib/archetypeNotes.ts`).
    - Summary per archetype, head to head, and spectra by archetype, all with the MR band filter.
    - `GET /api/v1/analysis/archetypes?band=`; the old path redirects.
- Shared `BandFilter` component.
- **Nav:** "Sets" removed (the set list stays at `/sets`, linked from the home page); new labels Stats by MR, Stats by Character, Archetypes.
- **Home page:** latest reviewed sets sorted by `sets.reviewed_at` (first review time, new in the tools; older sets backfilled from their ingest time), with Reviewed and Played columns. Older snapshots fall back to the played date.
- Tests for the new endpoints; docs for the three pages, the bands and the project plan.

## 2026-11-26 (win rates on player profiles)
- Player profile: new **Win rate** section, one block per character played. It has game win rate vs opponent MR in 100-point bands (only bands with games) and vs each opponent character, with an all-games / ranked-only toggle, a character picker for multi-character players, dimmed rows under 5 games and a bar against 50%. New `GET /api/v1/players/{id}/winrates` (`context=ranked`), with a test.
- Docs: player profile page doc describes the section and the endpoint.

## 2026-11-26 (A.K.I. character card)
- About page: new "Learning a character from a stronger player" card (Broski vs Zastorial, A.K.I.: throw loops, fireball Drive Rush follow-ups, wiki move names; obs-0026 to obs-0028), and the A.K.I. batch's prediction accuracy (21 of 32) in "How well the reviews predict".
- Docs: Observations page doc lists 28 notes; About page doc notes the new card.
- About page: prediction accuracy recounted from the snapshot's graded predictions (74% of 182; 81% Medium, 31 of 31 High) against the higher-MR player (67% of 100 sets with both MRs).

## 2026-11-25 (MR over time)
- Player profile: **MR over time** chart, one line per character, from reviewed ranked games (MR before the first game, then after each game), with presets (Last day, Last week, Last month, Last phase, 90 days, Year, All), a From / To range, a character picker, a hover crosshair and a table view. New `GET /api/v1/players/{id}/mr` (`date_from`, `date_to`, `character`). Per-game changes come from the tools' new `games.p1/p2_mr_change` (observed from the next game, or sfbuff's Elo formula, K = 16, for a set's last game); older snapshots fall back to the formula.
- Publish config: optional `phases` (`[{"name", "start"}]`), copied to `snapshot_meta.phases`, drives "Last phase" (Buckler doesn't expose the current phase).

## 2026-11-25
- About page: counts updated for 154 complete sets (throws, combo Drive Rush cancels, counter hits and punish counters with per-game numbers; resource use is higher for the winner in 86% of sets); new "Spend super before the round ends" habit card; prediction accuracy recounted (74% of 111 blind predictions vs 70% for the higher-MR player).
- Docs: Observations page doc lists 25 notes (obs-0023 revises obs-0016; obs-0024 a punished reversal comes back; obs-0025 rounds lost with super); traits and About page docs updated to 154 sets.

## 2026-11-24 (later)
- Traits: `/analysis/traits?view=all|others|me`. `others` leaves out sets with the configured player (settings `me`); `me` compares the configured player's won sets with their lost sets (unpaired, MR-weighted means, `won` / `lost` counts, `n_won` / `n_lost` per row). The Traits page has a switch for the three views.
- Set detail: each player gets `baseline` (the configured player's set against their own previous 7 days, from the tools' new `player_baseline` table); the set page shows it as "vs their last 7 days". Publish copies `player_baseline` when the source has it.
- Docs: analysis-methods.md explains the spectra pool without the configured player, the player weighting, the personal baseline and the three traits views.

## 2026-11-24
- Docs: Observations page doc lists 18 notes for 130 compared sets (obs-0018: predictions pick the winner but undersell the margin).
- Traits page doc: sf6-meta-description.md now lives in shotokan-sf6/meta-docs.

## 2026-11-23
- Docs: Observations page doc lists 17 notes (obs-0014 to obs-0017: button economy, the average game, blind MR-based predictions, lessons under pressure).
- Docs: analysis-methods.md gains a Damage section (white health, the 23 Nov rescore) and the prediction-vs-MR baseline; traits, observations and About page docs updated (122 sets, 13 notes, obs-0010 revises obs-0004, About differs from the dashboards' tab); data-sync.md and README explain `observations_dir` (relative to the config; none without it). `publish/publish.json` is gitignored.
- About page updated with what the data now shows (122 complete sets): damage counts cashed-in white health; Drive is judged by what it buys (burnouts alone don't separate winners); "Block first" replaced by "Don't get opened up on wake-up"; new "Throw, and cash in your hits" habit; Drive Reversal note; spectra list fixed (eight scores, temperament on defense and offense).
- About page: new "What the data says" section (winner vs loser signals, Arjun's white health, prediction accuracy vs the higher-MR baseline, Observations page).

## 2026-11-22
- Player overview by character: a By character table and a Character picker for spectra and per-game stats (snapshot schema 1.2 adds `player_character`, built from the source's new per-game `game_stats`; older snapshots still load).
- Moved to the shotokan-sf6 organization (was shogberg/SF6-SHOTOKAN-WEB): image is now ghcr.io/shotokan-sf6/web; links to shotokan-sf6/tools and shotokan-sf6/mods.
- Project plan: idea for a standalone self-serve analytics app (like lpp / sfbuff.site) fed by your own replays.
- Players page next to Sets: pick a player to open their overview, or filter the full list (`/api/v1/players`).
- What winning players do: winner vs loser of each set, stat by stat, MR-weighted, with what stands out and archetype win rates (`/api/v1/analysis/traits`).
- About SHOTOKAN page, matching the review dashboards' About tab.
- Navigation: Players and About added; "Winning traits" renamed "What winning players do".
- nginx example: HTTP/2 enabled with `http2 on;` (the `listen ... http2` form is deprecated from nginx 1.25.1, e.g. Amazon Linux 2023).

## 2026-11-21
- Navigation: the main links show as buttons, with the current page marked.

## 2026-11-20
- Unfinished sets have no winner: shown as – and left out of win/loss.

## 2026-11-19
- Set search: find any player's sets by name or CFN ID, 25 per page.
- Fixed missing spectra for Full and Tournament reviews.
- README: Docker install and run notes, including Docker Desktop on Windows.
- Container scripts keep LF line endings on Windows checkouts.
- API accepts any `tournament_<side>` review doc.
- Build phases 1-2: publish pipeline, API, player pages and Docker image.
- Design docs and planning decisions.

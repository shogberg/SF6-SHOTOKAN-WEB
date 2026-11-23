# Changelog

Notable changes to SHOTOKAN Web, newest first. Every push adds its changes here.

## 2026-11-23
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

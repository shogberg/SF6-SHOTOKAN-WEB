# Changelog

Notable changes to SHOTOKAN Web, newest first. Every push adds its changes here.

## 2026-11-22
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

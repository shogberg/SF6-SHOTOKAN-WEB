# Project plan

## Phase 0: Design (this commit)
- [x] README, architecture, data model, data sync, analysis methods, page specs, deployment, plan.
- [ ] Confirm the open questions below.

## Phase 1: Data foundation (local, in the tools repo + publish/)
- [x] Predictions read from `review_docs` into a `predictions` table in the snapshot (no sf6.db change needed yet).
- [ ] Add the `predictions` table and the `observations` source to sf6.db (migration in the tools repo).
- [ ] Backfill opponent MR / league where the capture has it (capture v3.3+); mark older opponents MR unknown.
- [x] `publish/schema.sql` v1 and `publish.py` skeleton: copy source tables, drop private columns, write `snapshot_meta`.
- [x] Derive modules: `player_set` (archetype history), `player_profile`, `player_archetype_summary`, `player_spectra_by_result`, `player_deviation`, `set_summary`, `predictions`, `observations`. Head to head is computed in the API for now.
- [x] Validation step and `--dry-run`.

## Phase 2: Player section (MVP)
- [x] API: search, profile, archetypes, sets, set detail, head to head.
- [x] Frontend: home/search, profile, player sets, set detail, head to head; shared components (spectrum bar, archetype badge, set card, sample-size badge).
- [x] Deploy files: nginx example (`shotokan.hogberg.dev`, shared login, TLS), systemd unit, `swap_snapshot.sh`.
- [ ] Stand up the EC2 instance, DNS and certbot; first deploy.
- [ ] First real publish with the existing 25 sets (tested locally: 25 sets, 26 players).
- [x] Docker: `docker/Dockerfile` (multi-stage), `compose.yml`, `publish --out` local mode, synthetic demo snapshot, GitHub Actions build/test/push to GHCR on tags. *(The image build itself is first exercised by CI: Docker Hub isn't reachable from where this was written.)*
- **Milestone:** look up any player and set without building a dashboard, on the server and via `docker run` locally.

## Phase 3: General analysis
- [ ] Derive modules: `mr_band_stats`, `trait_success`, `archetype_matchups`, MR weighting and the Japan adjustment. *(2026-11-26: band, character and archetype stats are computed in the API from the snapshot instead of at publish; MR weighting inside a band and the Japan adjustment are still to do.)*
- [x] Pages: Stats by MR (first version 2026-11-26), What winning players do, Observations, Archetypes (first version 2026-11-26: notes, mix, head to head and spectra by MR band).
- [ ] Stats by MR: quartiles, a two-band compare view, MR weighting inside a band.
- [ ] Archetypes: the predicted-edge matrix and spectrum pairings (docs/pages/archetype-predictions.md), with a flag where prediction and result disagree.
- [ ] Prediction accuracy over time on the Archetypes and Observations pages.
- **Milestone:** band and trait pages useful once there are enough sets per band. Until then they show counts, not rates.

## Phase 4: Character matchups
- [ ] Design the page (scope in [pages/character-matchups.md](pages/character-matchups.md)).
- [ ] Derive `matchup_char`; link `matchup_notes`.
- [ ] Page and API (replace the placeholder). *(2026-11-26: Stats by Character started at `/matchups` with character vs character game win rates and the MR band filter; the per-pairing detail is still planned.)*

## Phase 5: Later ideas
- `players.region` and the Japan MR adjustment, once JP data is imported (region possibly read from replays).
- Public anonymized snapshot.
- Clip links (video timestamps) from set detail, if videos get hosted somewhere.
- Rank/MR trends over time per player.
- **User accounts:** per-user login to track chosen players, sets or goals. Means app-side auth and somewhere to store writes (likely MariaDB alongside the read-only snapshot).
- Moving the rest to MariaDB only if it helps then.
- **Idea: a standalone self-serve app** (in the spirit of lpp and sfbuff.site). Anyone feeds it their own replays (capture files, and/or replay IDs pulled from Buckler the way `buckler_replays.py` does) and gets analytics and progress tracking: damage sources, Drive economy, anti-airs, throws and techs, counter hits, spectra and their trend over time, by character and matchup. It reuses the analyzer and the snapshot schema but skips most of the coaching layer (hand-written reviews, coach lenses, predictions, the ML / model side). Open questions: running the analyzer for other people (local app vs upload), where their data lives, and Buckler cookie handling (each user's own, never stored server-side).

## Decisions
| Question | Decision (2026-11-19) |
|---|---|
| MR bands | Under Master · below 1400 · 1400-1599 · 1600-1699 · 1700-1799 · 1800-1999 · 2000+ (revised 2026-11-26; was Diamond and below · below 1400 · 1400-1600 · 1600-1800 · 1800-2000 · 2000+) |
| Region / Japan adjustment | Deferred. No JP data imported for now; region may later be read from replays. The rule stays documented. |
| Access | Private, one shared login (nginx basic auth). Per-user accounts later (phase 5). |
| Domain | `shotokan.hogberg.dev` |
| MR weights | Draft values in place; Sean to review. |

## Open questions
1. **MR weights:** review the draft weights in [analysis-methods.md](analysis-methods.md).
2. **Region from replays:** check whether the replay info carries a region or country field (capture v3.3 already lists the player object's fields under `player_fields`).

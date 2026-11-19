# Project plan

## Phase 0: Design (this commit)
- [x] README, architecture, data model, data sync, analysis methods, page specs, deployment, plan.
- [ ] Confirm the open questions below.

## Phase 1: Data foundation (local, in SF6-SHOTOKAN + publish/)
- [ ] Add `players.region`, the `predictions` table and the `observations` source to sf6.db (migration in SF6-SHOTOKAN).
- [ ] Backfill opponent MR / league where the capture has it (capture v3.3+); mark older opponents MR unknown.
- [ ] `publish/schema.sql` v1 and `publish.py` skeleton: copy source tables, drop private columns, write `snapshot_meta`.
- [ ] Derive modules: `player_profile`, `player_archetype_history`, `player_archetype_summary`, `set_summary`, `h2h_summary`.
- [ ] Validation step and `--dry-run`.

## Phase 2: Player section (MVP)
- [ ] API: search, profile, archetypes, sets, set detail, head to head.
- [ ] Frontend: home/search, profile, player sets, set detail, head to head; shared components (spectrum bar, archetype badge, set card, sample-size badge).
- [ ] Deploy: EC2 layout, systemd, nginx with basic auth, TLS, `swap_snapshot.sh`.
- [ ] First real publish with the existing 25 sets.
- **Milestone:** look up any player and set without building a dashboard.

## Phase 3: General analysis
- [ ] Derive modules: `mr_band_stats`, `trait_success`, `archetype_matchups`, MR weighting and the Japan adjustment.
- [ ] Pages: MR bands, What winning players do, Observations, Archetype matchups.
- [ ] Prediction accuracy over time on the Archetype matchups and Observations pages.
- **Milestone:** band and trait pages useful once there are enough sets per band. Until then they show counts, not rates.

## Phase 4: Character matchups
- [ ] Design the page (scope in [pages/character-matchups.md](pages/character-matchups.md)).
- [ ] Derive `matchup_char`; link `matchup_notes`.
- [ ] Page and API (replace the placeholder).

## Phase 5: Later ideas
- Public anonymized snapshot.
- Clip links (video timestamps) from set detail, if videos get hosted somewhere.
- Rank/MR trends over time per player.
- Moving to MariaDB if the site ever takes writes (accounts, comments).

## Open questions
1. **MR 1600-1800:** the brief lists 1200-1400, 1400-1600, 1800-2000 and 2000+. I've added a **1600-1800** band to close the gap. OK?
2. **Below 1200:** grouped into 1200-1400 for now (Master MR rarely goes that low). Separate band instead?
3. **Region:** the capture doesn't include it. Enter it by hand per player, or leave it unknown (no JP adjustment) unless set?
4. **Public or private:** recommended private (basic auth) to start, since profiles describe real players' leaks.
5. **Domain and TLS:** subdomain to use?
6. **Weights:** the MR weights in [analysis-methods.md](analysis-methods.md) are a starting point. Adjust?

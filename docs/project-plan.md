# Project plan

## Phase 0: Design (this commit)
- [x] README, architecture, data model, data sync, analysis methods, page specs, deployment, plan.
- [ ] Confirm the open questions below.

## Phase 1: Data foundation (local, in SF6-SHOTOKAN + publish/)
- [ ] Add the `predictions` table and the `observations` source to sf6.db (migration in SF6-SHOTOKAN).
- [ ] Backfill opponent MR / league where the capture has it (capture v3.3+); mark older opponents MR unknown.
- [ ] `publish/schema.sql` v1 and `publish.py` skeleton: copy source tables, drop private columns, write `snapshot_meta`.
- [ ] Derive modules: `player_profile`, `player_archetype_history`, `player_archetype_summary`, `set_summary`, `h2h_summary`.
- [ ] Validation step and `--dry-run`.

## Phase 2: Player section (MVP)
- [ ] API: search, profile, archetypes, sets, set detail, head to head.
- [ ] Frontend: home/search, profile, player sets, set detail, head to head; shared components (spectrum bar, archetype badge, set card, sample-size badge).
- [ ] Deploy to `shotokan.hogberg.dev`: EC2 layout, systemd, nginx with a shared login, TLS, `swap_snapshot.sh`.
- [ ] First real publish with the existing 25 sets.
- [ ] Docker: `docker/Dockerfile` (multi-stage), `compose.yml`, `publish --out` local mode, synthetic demo snapshot, GitHub Actions build/test/push to GHCR on tags.
- **Milestone:** look up any player and set without building a dashboard, on the server and via `docker run` locally.

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
- `players.region` and the Japan MR adjustment, once JP data is imported (region possibly read from replays).
- Public anonymized snapshot.
- Clip links (video timestamps) from set detail, if videos get hosted somewhere.
- Rank/MR trends over time per player.
- **User accounts:** per-user login to track chosen players, sets or goals. Means app-side auth and somewhere to store writes (likely MariaDB alongside the read-only snapshot).
- Moving the rest to MariaDB only if it helps then.

## Decisions
| Question | Decision (2026-11-19) |
|---|---|
| MR bands | Diamond and below · **below 1400** (all Master under 1400) · 1400-1600 · **1600-1800** · 1800-2000 · 2000+ |
| Region / Japan adjustment | Deferred. No JP data imported for now; region may later be read from replays. The rule stays documented. |
| Access | Private, one shared login (nginx basic auth). Per-user accounts later (phase 5). |
| Domain | `shotokan.hogberg.dev` |
| MR weights | Draft values in place; Sean to review. |

## Open questions
1. **MR weights:** review the draft weights in [analysis-methods.md](analysis-methods.md).
2. **Region from replays:** check whether the replay info carries a region or country field (capture v3.3 already lists the player object's fields under `player_fields`).

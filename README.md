# SHOTOKAN Web

**Strategic Hit-confirm Oracle for Tactics, Okizeme, Knockdowns And Neutral**: the web front end.

A searchable site over every Street Fighter 6 set SHOTOKAN has reviewed. It replaces building a new dashboard for each review: the analysis still happens locally (see [SF6-SHOTOKAN](https://github.com/shogberg/SF6-SHOTOKAN) and [SF6-SHOTOKAN-mods](https://github.com/shogberg/SF6-SHOTOKAN-mods)), then a snapshot of the results is published here.

> Status: **phase 2 built**. The publish step, API, player pages, Docker image and deploy files exist; the general-analysis pages (phase 3) and character matchups (phase 4) are placeholders. See [docs/project-plan.md](docs/project-plan.md).
>
> Site: `shotokan.hogberg.dev` (private, shared login).

## Quick start

**Try it with demo data (Docker):**
```
docker run --rm -p 8080:8080 ghcr.io/shogberg/sf6-shotokan-web serve --demo
```
Open http://localhost:8080. The demo is synthetic: made-up players and sets.

**Use your own data (Docker):**
```
docker run --rm -v "D:\SF6-Claude-Coaching\history:/src:ro" -v shotokan-data:/data ghcr.io/shogberg/sf6-shotokan-web publish --source /src/sf6.db --out /data
docker run -d -p 8080:8080 -v shotokan-data:/data ghcr.io/shogberg/sf6-shotokan-web
```

**Without Docker (development):**
```
pip install -r api/requirements-dev.txt
python publish/publish.py --source path/to/sf6.db --out ./data [--config publish.json]
cd api && SHOTOKAN_DB=../data/current.db uvicorn app.main:app --port 8100       # API on :8100, docs at /api/docs
cd web && npm ci && npm run dev                                                  # site on :5173, proxies /api
python -m pytest -q api/tests                                                    # tests run on the demo data
```

**Publish to the server:** `python publish/publish.py --source sf6.db --target shotokan@shotokan.hogberg.dev:/srv/shotokan/data`. See [docs/data-sync.md](docs/data-sync.md) and [docs/deployment.md](docs/deployment.md).

**Publish config** (optional, keep it outside the repo, see `publish/publish.example.json`): `merge` folds a name used in local matches into the CFN player it belongs to (e.g. a local "shog" into ".shog"); `observations_dir` points at your observation notes; `anonymize` replaces opponent names with aliases.

## What the site does

### Players
Search by player name or CFN ID, then:

| View | What it shows |
|---|---|
| **Profile** | Archetype and lean, the eight spectra, strengths and weaknesses, per-game numbers, and how their archetype holds up: in winning vs losing sets, how often they deviate from their usual archetype, and in which direction. |
| **Sets** | Every set they've played: date, opponent, characters, result, review level, MR at the time. |
| **Set detail** | One set: games and rounds, the prediction made before review (if any) and how it graded, story, habits, Drive economy, hits. |
| **Head to head** | All sets between two players (e.g. .shog vs jon): record, how each played the other, what changed over time. |

### Character matchups *(placeholder, later phase)*
All games of one character pairing (e.g. Cammy vs Blanka) across every player. Planned, not designed yet.

### General analysis
| View | What it shows |
|---|---|
| **MR bands** | How players differ by skill band: Diamond and below (no MR), below 1400, 1400-1600, 1600-1800, 1800-2000, 2000+. |
| **What winning players do** | Typical archetypes and spectra of successful players, weighted toward higher MR. |
| **Observations** | Written notes on what makes a winning or struggling player, dated, so changes in the model over time stay visible. |
| **Archetype matchups** | Predicted and observed results when archetypes and spectra meet (e.g. Impulsive defense vs heavy frame-trap offense). |

## How it fits together

```
 local PC (Windows)                                   EC2
 ───────────────────                                  ───────────────────────────
 SF6 + REFramework ─► capture JSON                    nginx ─┬─ static site (built frontend)
 SF6-SHOTOKAN tools ─► sf6.db (full, private)                └─ /api ─► FastAPI (uvicorn)
 publish.py ─► shotokan_web.db (snapshot) ──scp/rsync──►               │ read-only
                                                      /srv/shotokan/data/current.db (SQLite)
```

- **Datastore: a read-only SQLite snapshot.** The local tools already write SQLite, the site only reads, and there's one writer (your PC). Publishing means building a snapshot file and swapping it in atomically: no SQL dumps to convert and no database server to run or secure. MariaDB stays an option if the site ever needs to accept writes (accounts, comments); the API's data layer is written so that switch is contained. See [docs/architecture.md](docs/architecture.md).
- **Backend:** Python (FastAPI), so it can reuse the spectra and profile logic from SF6-SHOTOKAN.
- **Frontend:** Svelte + Vite, built to static files that nginx serves. Node is only needed at build time.
- **Docker:** the whole site ships as one container image (`ghcr.io/shogberg/sf6-shotokan-web`), so anyone can run it locally against their own data, or a synthetic demo. The publish step runs from the same image. See [docs/docker.md](docs/docker.md).
- **Modular:** each section is its own API router, query module and frontend route folder. Adding a section means adding files, not editing a monolith.

## Docs
| Doc | Covers |
|---|---|
| [Architecture](docs/architecture.md) | Stack, why SQLite, repo layout, API conventions |
| [Data model](docs/data-model.md) | Snapshot schema: source tables, derived tables, new fields needed |
| [Data sync](docs/data-sync.md) | Getting data from the local PC to the server |
| [Analysis methods](docs/analysis-methods.md) | MR bands, the Japan MR adjustment, weighting, archetype deviation, confidence and sample sizes |
| [Pages](docs/pages/) | One spec per view |
| [Docker](docs/docker.md) | Container image, running locally, demo data, releases |
| [Deployment](docs/deployment.md) | EC2, nginx, systemd or container, TLS, backups |
| [Project plan](docs/project-plan.md) | Phases, milestones and open questions |

## Related repos
- [SF6-SHOTOKAN](https://github.com/shogberg/SF6-SHOTOKAN): analysis tooling and the local database.
- [SF6-SHOTOKAN-mods](https://github.com/shogberg/SF6-SHOTOKAN-mods): REFramework capture scripts and move names.

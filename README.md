# SHOTOKAN Web

**Strategic Hit-confirm Oracle for Tactics, Okizeme, Knockdowns And Neutral**: the web front end.

A searchable site over every Street Fighter 6 set SHOTOKAN has reviewed. It replaces building a new dashboard for each review: the analysis still happens locally (see [shotokan-sf6/tools](https://github.com/shotokan-sf6/tools) and [shotokan-sf6/mods](https://github.com/shotokan-sf6/mods)), then a snapshot of the results is published here.

> Status: **phase 2 built**. The publish step, API, player pages, Docker image and deploy files exist; the general-analysis pages (phase 3) and character matchups (phase 4) are placeholders. See [docs/project-plan.md](docs/project-plan.md).
>
> Site: `shotokan.hogberg.dev` (private, shared login).

## Quick start

### Docker (Docker Desktop on Windows or macOS, or Docker on Linux)
The image is a standard Linux image (amd64 and arm64), so Docker Desktop with the WSL 2 backend runs it as-is.

**1. Get the image.** Tagged releases are published to `ghcr.io/shotokan-sf6/web`:
```powershell
docker pull ghcr.io/shotokan-sf6/web
```
Before the first release (or to run your own changes), build it from a clone instead. Tagging it with the registry name means the commands below work unchanged:
```powershell
git clone https://github.com/shotokan-sf6/web
cd web
docker build -f docker/Dockerfile -t ghcr.io/shotokan-sf6/web .
```

**2. Try it with demo data:**
```powershell
docker run --rm -p 8080:8080 ghcr.io/shotokan-sf6/web serve --demo
```
Open http://localhost:8080. The demo is synthetic: made-up players and sets.

**3. Use your own data.** Build a snapshot from your `sf6.db` into a Docker volume, then start the site (PowerShell; the backtick continues the line):
```powershell
docker run --rm -v "D:\SF6-Claude-Coaching\history:/src:ro" -v "D:\SF6-Claude-Coaching:/cfg:ro" -v shotokan-data:/data `
  ghcr.io/shotokan-sf6/web publish --source /src/sf6.db --out /data --config /cfg/shotokan-publish.json
docker run -d --name shotokan -p 8080:8080 -v shotokan-data:/data ghcr.io/shotokan-sf6/web
```
Then open http://localhost:8080. After new reviews, run the publish command again: the running site picks up the new snapshot without a restart. `--config` is optional (see "Publish config" below).

**Or with compose:**
```powershell
$env:SF6_HISTORY_DIR = "D:\SF6-Claude-Coaching\history"
docker compose -f docker/compose.yml run --rm publish      # build a snapshot
docker compose -f docker/compose.yml up -d                 # start the site
```
For the demo instead: `$env:SHOTOKAN_ARGS = "--demo"` before `up -d`.

**Windows notes**
- Quote `D:\` paths in `-v`. With the WSL 2 backend, every drive can be mounted.
- Keep the site's data in the named volume (`shotokan-data`) rather than a Windows folder. It's faster, and the snapshot swap works as designed. (A Windows folder also works: publish falls back to copying the file.)
- Clone with git as usual. `.gitattributes` keeps the container scripts in Linux line endings so they run inside the container.
- Optional login when running without nginx: set `-e SHOTOKAN_AUTH=user:<sha256 of password>` on the `docker run` for the site.

### Without Docker (development)
```
pip install -r api/requirements-dev.txt
python publish/publish.py --source path/to/sf6.db --out ./data [--config publish.json]
cd api && SHOTOKAN_DB=../data/current.db uvicorn app.main:app --port 8100       # API on :8100, docs at /api/docs
cd web && npm ci && npm run dev                                                  # site on :5173, proxies /api
python -m pytest -q api/tests                                                    # tests run on the demo data
```

**Publish to the server:** `python publish/publish.py --source sf6.db --target shotokan@shotokan.hogberg.dev:/srv/shotokan/data`. See [docs/data-sync.md](docs/data-sync.md) and [docs/deployment.md](docs/deployment.md).

Sets the tools mark `excluded` (e.g. 1v1me betting matches) are left out of the snapshot, and flagged players (`player_flags`) get a profile badge.

**Publish config** (optional, keep it outside the repo, see `publish/publish.example.json`): `merge` folds a name used in local matches into the CFN player it belongs to (e.g. a local "shog" into ".shog"); `observations_dir` points at your observation notes (relative to the config file, or absolute; leave it out and the Observations page is empty); `anonymize` replaces opponent names with aliases.

## What the site does

### Players
Search by player name or CFN ID, then:

| View | What it shows |
|---|---|
| **Profile** | Badges for flagged players (Notable player; AZFGC with an Arizona flag). MR over time, one step per game. Game win rates per character played, against opponent MR (100-point bands) and against each opponent character. Archetype and lean, the eight spectra, strengths and weaknesses, per-game numbers, and how their archetype holds up: in winning vs losing sets, how often they deviate from their usual archetype, and in which direction. |
| **Sets** | Every set they've played: date, opponent, characters, result, review level, MR at the time. |
| **Set search** | Search any player by name or CFN ID, pick from the matching players, and page through all their sets, 25 per page (or browse every set). Not in the nav; linked from the home page, whose latest sets are sorted by review date. |
| **Set detail** | One set: games and rounds, the prediction made before review (if any) and how it graded, story, habits, Drive economy, hits. |
| **Head to head** | All sets between two players (e.g. .shog vs jon): record, how each played the other, what changed over time. |

### Stats by Character
Game win rates of every character against every other, filtered by set type (ranked by default, other, all) and by MR band. The per-pairing detail (damage each way, starters, punishes) is still planned.

### General analysis
| View | What it shows |
|---|---|
| **Stats by MR** | How players differ by skill band (Under Master, below 1400, 1400-1599, 1600-1699, 1700-1799, 1800-1999, 2000+): button economy, Drive economy, offense / pressure / oki, defense, damage taken, spectra and archetype mix, with dated notes. Ranked sets by default. |
| **What winning players do** | Typical archetypes and spectra of successful players, weighted toward higher MR. |
| **Observations** | Written notes on what makes a winning or struggling player, dated, so changes in the model over time stay visible. |
| **Archetypes** | What each archetype looks like and why players lean that way; share, set win rate, common characters, head to head and spectra by archetype, filtered by set type (ranked by default) and MR band. The predicted-edge matrix is still planned. |

## How it fits together

```
 local PC (Windows)                                   EC2
 ───────────────────                                  ───────────────────────────
 SF6 + REFramework ─► capture JSON                    nginx ─┬─ static site (built frontend)
 tools repo ─► sf6.db (full, private)                └─ /api ─► FastAPI (uvicorn)
 publish.py ─► shotokan_web.db (snapshot) ──scp/rsync──►               │ read-only
                                                      /srv/shotokan/data/current.db (SQLite)
```

- **Datastore: a read-only SQLite snapshot.** The local tools already write SQLite, the site only reads, and there's one writer (your PC). Publishing means building a snapshot file and swapping it in atomically: no SQL dumps to convert and no database server to run or secure. MariaDB stays an option if the site ever needs to accept writes (accounts, comments); the API's data layer is written so that switch is contained. See [docs/architecture.md](docs/architecture.md).
- **Backend:** Python (FastAPI), so it can reuse the spectra and profile logic from the tools repo (shotokan-sf6/tools).
- **Frontend:** Svelte + Vite, built to static files that nginx serves. Node is only needed at build time.
- **Docker:** the whole site ships as one container image (`ghcr.io/shotokan-sf6/web`), so anyone can run it locally against their own data, or a synthetic demo. The publish step runs from the same image. See [docs/docker.md](docs/docker.md).
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
- [shotokan-sf6/tools](https://github.com/shotokan-sf6/tools): analysis tooling and the local database.
- [shotokan-sf6/mods](https://github.com/shotokan-sf6/mods): REFramework capture scripts and move names.

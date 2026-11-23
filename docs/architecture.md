# Architecture

## Goals
- Look anything up without building a new dashboard per review.
- Keep the analysis where it already runs (the local PC), and keep the server simple.
- Split each section into its own files so the codebase grows by adding modules, not by editing a few giant ones.

## Components

| Component | Choice | Why |
|---|---|---|
| Datastore | **SQLite, read-only snapshot** | See below. |
| API | **Python 3.12 + FastAPI**, served by uvicorn behind nginx | Same language as the SHOTOKAN tools repo, so spectra, profile and MR-band code can be shared rather than rewritten. Typed responses and auto-generated API docs. |
| Data access | **SQLAlchemy Core** (no ORM) with plain SQL per module | Readable queries; swapping SQLite for MariaDB later only touches the engine URL and a few dialect-specific queries. |
| Frontend | **Svelte (SvelteKit, static adapter) + Vite**, charts with d3 | Small output, one file per component, one folder per route. Built to static files, so the server needs no Node at runtime. |
| Web server | **nginx** (on EC2) | Serves the static build, proxies `/api` to uvicorn, handles TLS and caching. In the Docker image the API serves the static build itself, so a local run needs no nginx. |
| Packaging | **Docker image** on GHCR | One artifact for local runs and, optionally, the server. See [docker.md](docker.md). |

### Why SQLite rather than MariaDB
- **One writer, many readers.** All data is produced on the local PC. The site never writes, so a database server's concurrency features aren't needed.
- **No translation.** The local database is already SQLite. A snapshot is the same engine and schema, so there's no SQL-dump conversion, type mapping or charset issue.
- **Atomic publishing.** Upload `shotokan_web-<timestamp>.db`, check it, then point `current.db` at it. Readers either see the old snapshot or the new one, never a half-imported state. Rollback is re-pointing the link.
- **Small.** The full local database is about 7 MB today. Even with thousands of sets (mostly the per-hit tables), it stays in the hundreds of MB, well within SQLite's comfort zone for reads.
- **Nothing to secure or patch** beyond file permissions. Backups are copying a file.

**When to move to MariaDB:** if the site gains user accounts, comments, uploads from other people, or several writers. The plan keeps that door open (SQLAlchemy Core, no SQLite-only features in shared queries). MariaDB is already installed on the instance, so the switch would be: create the schema, change the publish step to load SQL (or use the same Python loader against a MariaDB URL), and change the engine URL.

Not chosen: **PostgreSQL** (great, but not installed, and nothing here needs it yet) and **DuckDB** (strong for analytics, but SQLite is simpler to serve and the heavy aggregation happens at publish time anyway).

## Where the computation happens
Heavy work happens **locally at publish time**, not per request:
- the publish step computes derived tables (player profiles, archetype history, MR-band stats, archetype-vs-archetype results) and writes them into the snapshot;
- the API mostly selects from derived tables and does light filtering and paging;
- anything that needs a judgement call (observations, reviewer overrides) is written locally and shipped as data.

This keeps the server cheap (a small EC2 instance is plenty) and makes each snapshot a reproducible record of what the model said at that time.

## Repository layout (planned)

```
web/
├── README.md
├── docs/                       design docs (this folder)
├── api/                        FastAPI app
│   ├── app/
│   │   ├── main.py             creates the app, mounts routers, nothing else
│   │   ├── db.py               engine (read-only), snapshot metadata
│   │   ├── settings.py         paths, CORS, cache headers
│   │   ├── routers/            one file per section, thin
│   │   │   ├── players.py      search, profile
│   │   │   ├── sets.py         set list, set detail
│   │   │   ├── head_to_head.py
│   │   │   ├── matchups.py     character matchups (placeholder)
│   │   │   ├── mr_bands.py
│   │   │   ├── traits.py       what winning players do
│   │   │   ├── observations.py
│   │   │   └── archetype_predictions.py
│   │   ├── queries/            SQL per section, mirrors routers/
│   │   └── schemas/            Pydantic response models, mirrors routers/
│   └── tests/
├── web/                        SvelteKit frontend
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.ts          typed fetch helpers
│   │   │   ├── components/     shared: SpectrumBar, ArchetypeBadge, SetCard, MrBandPicker, charts/
│   │   │   └── format.ts       rank labels, dates, set scores
│   │   └── routes/             one folder per view
│   │       ├── +page.svelte                      home + search
│   │       ├── players/[id]/+page.svelte         profile
│   │       ├── players/[id]/sets/+page.svelte
│   │       ├── sets/[setKey]/+page.svelte
│   │       ├── h2h/[a]/[b]/+page.svelte
│   │       ├── matchups/+page.svelte             placeholder
│   │       └── analysis/
│   │           ├── mr-bands/+page.svelte
│   │           ├── traits/+page.svelte
│   │           ├── observations/+page.svelte
│   │           └── archetype-predictions/+page.svelte
│   └── package.json
├── publish/                    runs on the local PC
│   ├── publish.py              build snapshot from sf6.db, validate, upload
│   ├── derive/                 one module per derived table
│   └── schema.sql              snapshot schema (versioned)
├── docker/
│   ├── Dockerfile              multi-stage: build web, then Python runtime serving API + static
│   └── compose.yml             local run + on-demand publish
├── .github/workflows/docker.yml  build, test and push the image on version tags
└── deploy/
    ├── nginx.conf.example
    ├── shotokan-api.service    systemd unit
    └── swap_snapshot.sh        atomic swap + reload on the server
```

Rule of thumb: a new section = one router + one queries module + one schema module + one route folder (+ one derive module if it needs a new derived table). No edits to unrelated sections.

## API conventions
- Read-only `GET` endpoints under `/api/v1/`.
- Every response includes `snapshot: {id, built_at, tool_versions}` so the page can show how fresh the data is.
- Lists are paged (`limit`, `cursor`) and filterable by date range, review level, ranked/casual, character and MR band where it makes sense.
- Small results carry `n` (sample size) and a `confidence` so the frontend can grey out thin data instead of hiding it.
- Responses are cacheable (`Cache-Control` keyed on snapshot ID); nginx can cache `/api` until the next publish.

Planned endpoints (detailed per page in [pages/](pages/)):

```
GET /api/v1/search?q=                       players by name, alias or CFN ID
GET /api/v1/players/{id}                    profile
GET /api/v1/players/{id}/archetypes         archetype history, by result, deviations
GET /api/v1/players/{id}/sets               set list (filters)
GET /api/v1/sets/{set_key}                  set detail (+ prediction)
GET /api/v1/h2h/{a}/{b}                     head to head
GET /api/v1/matchups/{char_a}/{char_b}      placeholder: 501 until phase 4
GET /api/v1/analysis/mr-bands               band comparison
GET /api/v1/analysis/traits                 traits of winning players
GET /api/v1/analysis/observations           dated notes
GET /api/v1/analysis/archetype-predictions  archetype / spectrum matrix
GET /api/v1/meta                            snapshot info, band definitions, glossary
```

## Access
The data is about real players (CFN names, habits, leaks), so the site is **private**: one shared login (nginx basic auth) for now. Per-user **accounts** are a later phase (e.g. to let each user track their own players or sets); that's also the point where the app gets its own auth and may move to MariaDB for the writes. The publish step can also export an "anonymized" snapshot that replaces opponent names with stable aliases, if you ever want a public version.

# Docker

SHOTOKAN Web ships as one container image, so anyone can run the site on their own PC against their own data. The same image can also run on the EC2 instance.

## The image
`ghcr.io/shogberg/sf6-shotokan-web:<version>` (also `:latest`), built from `docker/Dockerfile`:

```
stage 1  node:22-alpine     npm ci && npm run build            → web/build (static site)
stage 2  python:3.12-slim   pip install api + publish deps
                            copy api/, publish/, web/build → /app
                            non-root user, port 8080
```

At runtime the container runs **uvicorn** with FastAPI serving both `/api/v1/...` and the built static site (one process, no nginx inside the image). On EC2, nginx stays in front for TLS and the shared login; locally, nobody needs nginx.

| Setting (env var) | Default | Meaning |
|---|---|---|
| `SHOTOKAN_DB` | `/data/current.db` | Snapshot to serve (read-only). |
| `SHOTOKAN_PORT` | `8080` | Listen port. |
| `SHOTOKAN_AUTH` | *(unset)* | `user:password-hash` to turn on a shared login inside the app (for running without nginx). Unset = no login, fine on localhost. Never baked into the image. |
| `SHOTOKAN_BASE_URL` | `/` | If served under a sub-path. |

## Running it locally

### With your own data
1. Build a snapshot from your local database (the publish step can run in the same image, so you don't need Python installed):
   ```
   docker run --rm -v "D:\SF6-Claude-Coaching\history:/src:ro" -v shotokan-data:/data \
     ghcr.io/shogberg/sf6-shotokan-web publish --source /src/sf6.db --out /data
   ```
   `publish --out` builds, validates and swaps the snapshot into the volume, the same as the server-side swap, with no upload.
2. Start the site:
   ```
   docker run -d --name shotokan -p 8080:8080 -v shotokan-data:/data ghcr.io/shogberg/sf6-shotokan-web
   ```
3. Open http://localhost:8080.

### With docker compose
`docker/compose.yml` (planned):
```yaml
services:
  web:
    image: ghcr.io/shogberg/sf6-shotokan-web:latest
    ports: ["8080:8080"]
    volumes: ["shotokan-data:/data"]
    restart: unless-stopped
  publish:                    # run on demand: docker compose run --rm publish
    image: ghcr.io/shogberg/sf6-shotokan-web:latest
    command: publish --source /src/sf6.db --out /data
    volumes:
      - shotokan-data:/data
      - ${SF6_HISTORY_DIR}:/src:ro     # folder holding your sf6.db
    profiles: ["tools"]
volumes:
  shotokan-data:
```

### Demo data
For trying the site without any reviews of your own, the image can start with `--demo`. That loads a small **synthetic** snapshot (`publish/demo/`) with made-up players and sets in the real schema. Real players' data is never shipped in the image or the repo.

## Running the container on EC2 (option)
Instead of the systemd + venv setup in [deployment.md](deployment.md), the server can run the same image:
- `docker run -d --restart unless-stopped -p 127.0.0.1:8100:8080 -v /srv/shotokan/data:/data:ro ghcr.io/shogberg/sf6-shotokan-web:<version>`
- nginx keeps TLS and the shared login for `shotokan.hogberg.dev` and proxies everything to `127.0.0.1:8100`.
- `swap_snapshot.sh` is unchanged. The container sees the new `current.db` through the mounted folder and reopens it.

Both setups are supported. The plan is to start with whichever is quicker to stand up, likely the container, since it's the same artifact people run locally.

## Building and releasing
- `docker build -f docker/Dockerfile -t sf6-shotokan-web .` builds locally.
- A GitHub Actions workflow (`.github/workflows/docker.yml`, planned):
  - **on a version tag** (`v0.1.0`): build multi-arch (amd64, arm64; arm64 suits Graviton and Apple silicon), run the API tests against the demo snapshot, push to GHCR as `:<version>` and `:latest`;
  - **on pull requests**: build only, no push.
- The image's labels record the version, the snapshot schema version it supports, and the git commit.

## Compatibility
The image reads snapshots whose **major** schema version it knows (see [data-sync.md](data-sync.md)). If someone's snapshot is newer or older than the image supports, the site shows a clear message naming the versions instead of failing. `publish` in the same image always writes a version that image can read.

# Deployment (EC2)

Uses what's on the instance: nginx, Python, Node (build only). MariaDB isn't needed for the SQLite plan.

Two supported ways to run the API: **systemd + venv** (below), or **the Docker image** behind the same nginx (see [docker.md](docker.md#running-the-container-on-ec2-option)). Everything about the data folder, snapshot swap, TLS and the shared login is the same either way.

## Layout on the server
```
/srv/shotokan/
├── api/            git checkout (api/), Python venv in api/.venv
├── web/            built static site (copied from web/build)
└── data/
    ├── incoming/   uploads land here
    ├── snapshots/  last 5 snapshots
    └── current.db  → symlink to the live snapshot
```
Users: `shotokan` owns `/srv/shotokan`; the API runs as `shotokan-api`, with read-only access to `data/`.

## Services
- **API:** systemd unit `shotokan-api.service` runs `uvicorn app.main:app --host 127.0.0.1 --port 8100 --workers 2`. The SQLite file is opened read-only (`mode=ro`, `immutable=1` per snapshot file).
- **Snapshot swap:** `deploy/swap_snapshot.sh` checks the upload (integrity check, schema version), moves it into `snapshots/`, repoints `current.db`, and sends `systemctl reload shotokan-api` (or the API reopens when the link target changes).
- **Frontend:** `npm ci && npm run build` (locally or on the server), then rsync `web/build/` to `/srv/shotokan/web/`.

## nginx (sketch)
```
server {
    listen 443 ssl;
    http2 on;               # nginx 1.25.1+ (older: listen 443 ssl http2;)
    server_name shotokan.hogberg.dev;
    # ssl_certificate ... (Let's Encrypt via certbot)

    auth_basic "SHOTOKAN";                 # shared login while the site is private
    auth_basic_user_file /etc/nginx/shotokan.htpasswd;

    root /srv/shotokan/web;
    location / { try_files $uri $uri/ /index.html; }

    location /api/ {
        proxy_pass http://127.0.0.1:8100;
        proxy_set_header Host $host;
        proxy_cache_valid 200 10m;         # optional; snapshot ID is in each response
    }
}
```

## Security
- Security group: 443 (and 80 for the certbot redirect) open to where you want; SSH from your IP only.
- Shared login (basic auth, one htpasswd entry you hand out). Per-user accounts come later, in the app.
- DNS: an A record (or CNAME to the instance's Elastic IP) for `shotokan.hogberg.dev`; TLS from Let's Encrypt via certbot.
- No secrets in the repo: the htpasswd file and any env file live only on the server.
- Uploads over SSH key; the `shotokan` user can write only to `data/incoming`.

## Backups
The source of truth is the local `sf6.db` (back that up locally). The server keeps the last 5 snapshots; that's enough to roll back a bad publish.

## Sizing
A t3.small (or t4g.small) is plenty: the API serves precomputed rows from a file of a few MB.

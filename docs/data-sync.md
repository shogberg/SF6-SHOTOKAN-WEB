# Data sync: local PC → server

Data is produced on the local PC (captures, analyzer, reviews). The server only displays it. Sync is one command run locally after reviews: **build a snapshot, check it, upload it, swap it in.**

## The flow

```
1. review sets as today            → sf6.db (local, full)
2. python publish/publish.py       → builds snapshot  publish/out/shotokan_web-20261119-1145.db
                                    → validates it      (schema version, row counts, no private columns)
                                    → uploads it        scp/rsync to ec2:/srv/shotokan/data/incoming/
                                    → runs on server    deploy/swap_snapshot.sh
3. server: swap_snapshot.sh        → integrity check (PRAGMA integrity_check, schema version)
                                    → mv into data/snapshots/, repoint data/current.db symlink
                                    → signal the API to reopen (or it checks the link on each request)
                                    → keep the last 5 snapshots for rollback
```

## Why a whole-file snapshot instead of .sql files
- **Atomic:** the site never sees a half-imported state.
- **Simple:** no dump/restore and no dialect conversion. The file is the database.
- **Small enough:** a few MB today. Even at tens of MB, a full upload takes seconds; rsync only sends changed blocks.
- **Reproducible:** every snapshot records the tool versions and settings it was built with, so you can see what the model said at any point.

If the site ever moves to MariaDB, `publish.py` keeps the same "build → check → swap" shape. It would load the snapshot into a staging schema with the same Python loader, check it, then swap with `RENAME TABLE`. Still no hand-written SQL dumps.

## publish.py (planned)
```
python publish/publish.py \
  --source "D:\SF6-Claude-Coaching\history\sf6.db" \
  --target ec2-user@shotokan:/srv/shotokan/data \
  [--private]        # default: full names; --anonymize: aliases for opponents
  [--dry-run]        # build and validate only

# local target, no upload (also how the Docker image runs it):
python publish/publish.py --source sf6.db --out ./data
```
Steps:
1. Copy the source tables listed in [data-model.md](data-model.md), dropping private columns.
2. Run each `publish/derive/*.py` module in dependency order (profiles → archetype history → summaries → band stats → trait success → archetype matchups).
3. Write `snapshot_meta` and the `observations` (from `observations/*.md` in the SF6-SHOTOKAN repo or a local folder).
4. Validate: schema version matches the API's, every derived table non-empty, foreign keys resolve, a sample of profile numbers matches a direct recomputation.
5. Upload over SSH (key auth; no passwords in the script or config).
6. Run `swap_snapshot.sh` remotely and print the new snapshot ID.

## Credentials
- SSH key only, stored in the normal SSH agent or config. The publish config holds the host and path, never a password.
- Upload goes to a dedicated `shotokan` user that can write only to `/srv/shotokan/data/incoming`.

## Schema versions
- `publish/schema.sql` carries a version number; the API refuses a snapshot whose major version it doesn't know, and keeps serving the previous one.
- Adding a derived table is a minor version, and older API builds ignore it. Changing a column is a major version, so deploy the API first.

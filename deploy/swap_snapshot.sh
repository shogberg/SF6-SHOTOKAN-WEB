#!/bin/sh
# Install an uploaded snapshot atomically:  swap_snapshot.sh /srv/shotokan/data/incoming/shotokan_web-YYYYMMDD-HHMMSS.db
set -eu
SNAP="$1"; DATA="${SHOTOKAN_DATA:-/srv/shotokan/data}"; KEEP="${SHOTOKAN_KEEP:-5}"; MAJOR="1"; MIN_MINOR="1"
[ -f "$SNAP" ] || { echo "no such file: $SNAP"; exit 1; }
python3 - "$SNAP" "$MAJOR" "$MIN_MINOR" <<'PY'
import sqlite3, sys
con = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
assert con.execute("pragma integrity_check").fetchone()[0] == "ok", "integrity check failed"
v = dict(con.execute("select key, value from snapshot_meta"))["schema_version"]
ma, _, mi = v.partition(".")
assert ma == sys.argv[2] and int(mi or 0) >= int(sys.argv[3]), f"schema {v} not supported (expects {sys.argv[2]}.{sys.argv[3]}+)"
print("ok", v)
PY
mkdir -p "$DATA/snapshots"
NAME="$(basename "$SNAP")"
mv "$SNAP" "$DATA/snapshots/$NAME"
ln -sfn "snapshots/$NAME" "$DATA/current.db.new" && mv -T "$DATA/current.db.new" "$DATA/current.db"
ls -1 "$DATA/snapshots/"*.db | sort | head -n -"$KEEP" | xargs -r rm -f
echo "live: $NAME"   # the API reopens on its next request (it watches current.db)

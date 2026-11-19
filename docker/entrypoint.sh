#!/bin/sh
# shotokan serve            run the site (default)
# shotokan serve --demo     build a synthetic demo snapshot into /data first if none exists, then run
# shotokan publish ARGS     run publish.py (e.g. --source /src/sf6.db --out /data)
set -e
cmd="${1:-serve}"; [ $# -gt 0 ] && shift
case "$cmd" in
  serve)
    if [ "$1" = "--demo" ] && [ ! -e "$SHOTOKAN_DB" ]; then
      python /app/publish/demo/make_demo.py /tmp/demo_source.db
      python /app/publish/publish.py --source /tmp/demo_source.db --out "$(dirname "$SHOTOKAN_DB")"
    fi
    cd /app/api
    exec python -m uvicorn app.main:app --host 0.0.0.0 --port "$SHOTOKAN_PORT" --workers "${SHOTOKAN_WORKERS:-2}" --proxy-headers
    ;;
  publish) exec python /app/publish/publish.py "$@" ;;
  demo-source) exec python /app/publish/demo/make_demo.py "$@" ;;
  *) exec "$cmd" "$@" ;;
esac

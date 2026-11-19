"""SHOTOKAN Web API. Mounts one router per section; serves the built frontend when SHOTOKAN_STATIC is set."""
import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from . import settings, db
from .auth import SharedLogin
from .routers import meta, players, sets, head_to_head, matchups, analysis

app = FastAPI(title="SHOTOKAN Web", version="0.1.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
if settings.AUTH:
    app.add_middleware(SharedLogin)

for r in (meta, players, sets, head_to_head, matchups, analysis):
    app.include_router(r.router, prefix="/api/v1")


@app.exception_handler(db.SnapshotError)
def snapshot_error(request: Request, exc: db.SnapshotError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.middleware("http")
async def cache_headers(request: Request, call_next):
    resp = await call_next(request)
    if request.url.path.startswith("/api/v1/") and resp.status_code == 200:
        resp.headers["Cache-Control"] = "private, max-age=60"
    return resp


@app.get("/healthz", include_in_schema=False)
def healthz():
    try:
        return {"ok": True, "snapshot": db.meta()}
    except db.SnapshotError as e:
        return JSONResponse(status_code=503, content={"ok": False, "detail": str(e)})


if settings.STATIC_DIR and os.path.isdir(settings.STATIC_DIR):
    static = settings.STATIC_DIR
    app.mount("/_app", StaticFiles(directory=os.path.join(static, "_app")), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        f = os.path.normpath(os.path.join(static, path))
        if path and f.startswith(os.path.abspath(static)) and os.path.isfile(f):
            return FileResponse(f)
        return FileResponse(os.path.join(static, "index.html"))

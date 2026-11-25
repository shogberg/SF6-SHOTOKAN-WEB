"""Read-only access to the current snapshot. Reopens automatically when current.db is swapped."""
import os, threading
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from . import settings

_lock = threading.Lock()
_state = {"key": None, "engine": None, "meta": None}


class SnapshotError(RuntimeError):
    pass


def _key(path):
    real = os.path.realpath(path)
    st = os.stat(real)
    return real, st.st_mtime_ns, st.st_size


def engine():
    path = settings.DB_PATH
    if not os.path.exists(path):
        raise SnapshotError(f"no snapshot at {path}: run publish first (see docs/data-sync.md)")
    k = _key(path)
    with _lock:
        if _state["key"] != k:
            real = k[0]
            eng = create_engine(f"sqlite:///file:{real}?mode=ro&uri=true", poolclass=NullPool, future=True)
            with eng.connect() as c:
                meta = dict(c.execute(text("select key, value from snapshot_meta")).all())
            ver = str(meta.get("schema_version", "0.0"))
            major, _, minor = ver.partition(".")
            if major != settings.SUPPORTED_MAJOR or int(minor or 0) < settings.MIN_MINOR:
                raise SnapshotError(f"snapshot schema {ver} not supported (this build reads {settings.SUPPORTED_MAJOR}.{settings.MIN_MINOR} or newer "
                                    f"{settings.SUPPORTED_MAJOR}.x): run publish again with this version")
            _state.update(key=k, engine=eng, meta=meta)
        return _state["engine"]


def meta():
    engine()
    m = _state["meta"]
    return {"id": m.get("snapshot_id"), "built_at": m.get("built_at"), "schema_version": m.get("schema_version"),
            "anonymized": m.get("anonymized") == "True"}


def rows(sql, **params):
    with engine().connect() as c:
        return [dict(r._mapping) for r in c.execute(text(sql), params)]


def one(sql, **params):
    r = rows(sql, **params)
    return r[0] if r else None


def meta_value(key, default=None):
    """One raw snapshot_meta value (e.g. 'phases'), or default."""
    engine()
    return _state["meta"].get(key, default)

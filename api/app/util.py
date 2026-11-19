import json
from fastapi import HTTPException
from . import db


def wrap(data, **extra):
    return {"snapshot": db.meta(), "data": data, **extra}


def loads(v, default=None):
    if v in (None, ""):
        return default
    try:
        return json.loads(v)
    except (TypeError, ValueError):
        return default


PER_PAGE = 25
MAX_PER_PAGE = 100


def paginate(rows, page=1, per_page=PER_PAGE):
    """Slice a list into one page. Lists here are small (one player's sets), so filtering happens first, in SQL."""
    per_page = max(1, min(int(per_page or PER_PAGE), MAX_PER_PAGE))
    total = len(rows)
    pages = max(1, -(-total // per_page))
    page = max(1, min(int(page or 1), pages))
    start = (page - 1) * per_page
    return rows[start:start + per_page], {"page": page, "per_page": per_page, "total": total, "pages": pages}


def not_found(what):
    raise HTTPException(status_code=404, detail=f"{what} not found")


def planned(phase, what):
    raise HTTPException(status_code=501, detail={"status": "planned", "phase": phase, "what": what})

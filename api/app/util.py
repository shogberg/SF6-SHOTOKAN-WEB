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


def not_found(what):
    raise HTTPException(status_code=404, detail=f"{what} not found")


def planned(phase, what):
    raise HTTPException(status_code=501, detail={"status": "planned", "phase": phase, "what": what})

from fastapi import APIRouter
from .. import db
from ..util import wrap, loads
from ..queries import sets as Q

router = APIRouter(tags=["meta"])


@router.get("/meta")
def meta():
    m = {r["key"]: r["value"] for r in db.rows("select key, value from snapshot_meta")}
    counts = {t: db.one(f"select count(*) as n from {t}")["n"] for t in ("players", "sets", "games", "hits")}
    return wrap({"bands": loads(m.get("bands"), []), "jp_adjustment": m.get("jp_adjustment"), "counts": counts,
                 "recent_sets": Q.recent()})

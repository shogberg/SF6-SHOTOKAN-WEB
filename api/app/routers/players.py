from fastapi import APIRouter, Query
from ..util import wrap, not_found, paginate, loads, PER_PAGE
from ..queries import players as Q

router = APIRouter(tags=["players"])


@router.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(20, le=50)):
    return wrap(Q.search(q, limit))


@router.get("/players")
def players():
    r = Q.list_all()
    for p in r:
        p["characters"] = loads(p["characters"], [])
    return wrap(r)


@router.get("/players/{pid}")
def profile(pid: int):
    p = Q.profile(pid)
    return wrap(p) if p else not_found("player")


@router.get("/players/{pid}/archetypes")
def archetypes(pid: int):
    if not Q.profile(pid):
        not_found("player")
    return wrap(Q.archetypes(pid))


@router.get("/players/{pid}/sets")
def sets(pid: int, opponent: int | None = None, character: str | None = None, result: str | None = None, review: str | None = None,
         context: str | None = None, band: str | None = None, date_from: str | None = None, date_to: str | None = None,
         page: int = 1, per_page: int = PER_PAGE):
    if not Q.profile(pid):
        not_found("player")
    r = Q.sets(pid, opponent=opponent, character=character, result=result, review=review, context=context, band=band,
               date_from=date_from, date_to=date_to)
    totals = {"sets": len(r), "won": sum(x["won"] or 0 for x in r), "lost": sum(1 for x in r if x["won"] == 0), "games_won": sum(x["games_won"] or 0 for x in r),
              "games_lost": sum(x["games_lost"] or 0 for x in r)}
    data, pg = paginate(r, page, per_page)
    return wrap(data, totals=totals, page=pg)

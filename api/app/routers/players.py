from fastapi import APIRouter, Query
from ..util import wrap, not_found, paginate, loads, PER_PAGE
from ..queries import players as Q
from ..db import meta_value

router = APIRouter(tags=["players"])


@router.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(20, le=50)):
    return wrap(Q.search(q, limit))


@router.get("/players")
def players():
    r = Q.list_all()
    fl = Q.flags_by_player()
    for p in r:
        p["characters"] = loads(p["characters"], [])
        p["flags"] = fl.get(p["player_id"], [])
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


@router.get("/players/{pid}/mr")
def mr(pid: int, date_from: str | None = None, date_to: str | None = None, character: str | None = None):
    """MR over time (reviewed ranked games). `characters` lists every character with MR points, in first-played order,
    so colours stay fixed when a filter narrows the points; `phases` are the ranked phase start dates from the publish config."""
    if not Q.profile(pid):
        not_found("player")
    pts, chars = Q.mr_history(pid, date_from=date_from, date_to=date_to, character=character)
    phases = loads(meta_value("phases"), [])
    return wrap(pts, characters=chars, phases=phases)


@router.get("/players/{pid}/winrates")
def winrates(pid: int, context: str | None = None):
    """Game win rates per character played: by the opponent's MR (100-point bands, games where the opponent had an MR)
    and by opponent character. `context=ranked` keeps ranked sets only."""
    if not Q.profile(pid):
        not_found("player")
    return wrap(Q.win_rates(pid, context=context))


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

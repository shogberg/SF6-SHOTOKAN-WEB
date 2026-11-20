from fastapi import APIRouter, Query
from ..util import wrap, not_found, paginate, PER_PAGE
from ..queries import sets as Q
from ..queries import players as P

router = APIRouter(tags=["sets"])


@router.get("/sets")
def list_sets(q: str | None = Query(None, description="player name, past name or CFN ID"),
              player: int | None = Query(None, description="player_id (wins over q)"),
              result: str | None = None, review: str | None = None, context: str | None = None,
              page: int = 1, per_page: int = PER_PAGE):
    """Sets as a paged list. With a player (or a q that matches exactly one player): that player's sets, from their side.
    With a q that matches several players: the candidates to choose from, and no sets yet. With neither: every set."""
    candidates = []
    if player is None and q and q.strip():
        candidates = P.search(q, 20)
        exact = [c for c in candidates if c["name"].lower() == q.strip().lower() or (c["cfn_id"] or "") == q.strip()]
        if len(exact) == 1:
            player = exact[0]["player_id"]
        elif len(candidates) == 1:
            player = candidates[0]["player_id"]
        else:
            return wrap([], candidates=candidates, player=None, totals=None,
                        page={"page": 1, "per_page": per_page, "total": 0, "pages": 1})
    if player is not None:
        prof = P.profile(player)
        if not prof:
            not_found("player")
        r = P.sets(player, result=result, review=review, context=context)
        totals = {"sets": len(r), "won": sum(x["won"] or 0 for x in r), "lost": sum(1 for x in r if x["won"] == 0), "games_won": sum(x["games_won"] or 0 for x in r),
                  "games_lost": sum(x["games_lost"] or 0 for x in r)}
        data, pg = paginate(r, page, per_page)
        return wrap(data, candidates=candidates, totals=totals, page=pg,
                    player={"player_id": prof["player_id"], "name": prof["name"], "cfn_id": prof["cfn_id"], "characters": prof["characters"]})
    r = [x for x in Q.all_sets() if (not review or x["review"] == review) and (not context or x["context"] == context)]
    data, pg = paginate(r, page, per_page)
    return wrap(data, candidates=[], player=None, totals={"sets": len(r)}, page=pg)


@router.get("/sets/{set_key}")
def detail(set_key: str):
    d = Q.detail(set_key)
    return wrap(d) if d else not_found("set")

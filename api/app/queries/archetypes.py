"""Archetypes: how the four archetype reads (Aggressive, Balanced, Defensive, Fundamentalist) are spread, how they do,
and how they do against each other (docs/pages/archetype-predictions.md). The unit is a player-set with a read.
A band filter keeps player-sets whose player was in that MR band at the set; in the head-to-head table the filter
applies to the row player."""
from collections import defaultdict, Counter
from statistics import mean
from ..db import rows
from .traits import HIGH_END
from .mr_bands import context_ok

MAIN = ["Aggressive", "Balanced", "Defensive", "Fundamentalist"]


def _arch(a):
    a = (a or "").split()[0].strip(",/") if a else ""
    return a if a in MAIN else None


def archetypes(band=None, context="all"):
    """context: 'ranked', 'other' (casual, custom room, local, tournament, unknown) or 'all'."""
    band = None if band in (None, "", "all") else band
    ps = rows("""select ps.set_key, ps.player_id, ps.opp_id, ps.band, ps.archetype, ps.lean, ps.opp_archetype, ps.won, ps.character, ps.context
                 from player_set ps""")
    ps = [p for p in ps if context_ok(p["context"], context)]
    sel = [p for p in ps if _arch(p["archetype"]) and (band is None or p["band"] == band)]
    by = defaultdict(list)
    for p in sel:
        by[_arch(p["archetype"])].append(p)
    tot = len(sel)
    spec = defaultdict(lambda: defaultdict(list))
    keys = {(p["set_key"], p["player_id"]): _arch(p["archetype"]) for p in sel}
    for r in rows("select set_key, player_id, axis, score from spectra"):
        a = keys.get((r["set_key"], r["player_id"]))
        if a and r["score"] is not None:
            spec[a][r["axis"]].append(r["score"])
    summary = []
    for a in MAIN:
        xs = by.get(a, [])
        dec = [p for p in xs if p["won"] is not None]
        chars = Counter(p["character"] for p in xs if p["character"])
        leans = Counter((p["lean"] or "").strip() for p in xs if p["lean"])
        summary.append({
            "archetype": a, "player_sets": len(xs), "share_pct": round(100 * len(xs) / tot) if tot else None,
            "decided": len(dec), "won": sum(1 for p in dec if p["won"]), "win_pct": round(100 * sum(1 for p in dec if p["won"]) / len(dec)) if dec else None,
            "players": len({p["player_id"] for p in xs}),
            "top_characters": [{"character": c, "n": n} for c, n in chars.most_common(5)],
            "top_leans": [{"lean": l, "n": n} for l, n in leans.most_common(4)],
            "spectra": [{"axis": ax, "high_end": HIGH_END[ax], "mean": round(mean(spec[a][ax]), 2) if spec[a][ax] else None, "n": len(spec[a][ax])}
                        for ax in HIGH_END],
        })
    vs = defaultdict(lambda: [0, 0])
    for p in sel:
        a, b = _arch(p["archetype"]), _arch(p["opp_archetype"])
        if b and p["won"] is not None:
            vs[(a, b)][1] += 1
            vs[(a, b)][0] += 1 if p["won"] else 0
    matrix = [{"archetype": a, "opp_archetype": b, "sets": v[1], "won": v[0], "win_pct": round(100 * v[0] / v[1]) if v[1] else None}
              for (a, b), v in sorted(vs.items())]
    return {"band": band or "all", "context": context or "all", "player_sets": tot, "summary": summary, "matrix": matrix}

"""Stats by character: game win rates for each character against every other character (docs/pages/character-matchups.md).

Every decided game counts from both sides: player A's character vs B's, and B's vs A's. A band filter keeps the side
whose player was in that MR band at the set (player_set.band), so "Cammy vs Sagat at 1600-1699" means games where the
Cammy player was 1600-1699, whatever the Sagat player's MR. Mirror matches count as games but have no win rate."""
from collections import defaultdict
from ..db import rows
from .mr_bands import _bands


def bands():
    return [{"id": "all", "label": "All"}] + [{"id": b["id"], "label": b["label"]} for b in _bands()]


def character_stats(band=None):
    band = None if band in (None, "", "all") else band
    pb = {(r["set_key"], r["player_id"]): r["band"] for r in rows("select set_key, player_id, band from player_set")}
    games = rows("""select g.set_key, g.p1_player_id as a, g.p2_player_id as b, g.p1_char as ca, g.p2_char as cb, g.winner_player_id as w
                    from games g where g.winner_player_id is not null and g.p1_char is not null and g.p2_char is not null""")
    m = defaultdict(lambda: defaultdict(lambda: [0, 0]))   # char -> opp char -> [won, games]
    for g in games:
        for me, opp, c, oc in ((g["a"], g["b"], g["ca"], g["cb"]), (g["b"], g["a"], g["cb"], g["ca"])):
            if band and pb.get((g["set_key"], me)) != band:
                continue
            cell = m[c][oc]
            cell[1] += 1
            cell[0] += 1 if g["w"] == me else 0
    out = []
    for c, opps in m.items():
        non_mirror = [(oc, v) for oc, v in opps.items() if oc != c]
        won = sum(v[0] for _oc, v in non_mirror)
        n = sum(v[1] for _oc, v in non_mirror)
        out.append({
            "character": c, "games": sum(v[1] for v in opps.values()), "games_non_mirror": n, "won": won, "lost": n - won,
            "win_pct": round(100 * won / n) if n else None,
            "vs": sorted(({"opp_character": oc, "games": v[1], "won": v[0] if oc != c else None, "lost": (v[1] - v[0]) if oc != c else None,
                           "win_pct": (round(100 * v[0] / v[1]) if v[1] else None) if oc != c else None, "mirror": oc == c}
                          for oc, v in opps.items()), key=lambda x: (-x["games"], x["opp_character"])),
        })
    out.sort(key=lambda x: (-x["games"], x["character"]))
    return out

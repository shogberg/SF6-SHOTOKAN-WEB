"""player_set: one row per player per set (MR band at the time, archetype read, result, deviation flag)."""
import collections
from common import parse_rank, band_for, weight_for


def context_of(s):
    note = (s["note"] or "").lower()
    if s["ranked"] == 1:
        return "ranked"
    if "local" in note:
        return "local"
    if "tournament" in note:
        return "tournament"
    if "casual" in note or "custom room" in note:
        return "casual"
    return "unknown"


def mr_at_set(con, set_key, pid, s):
    for g in con.execute("select * from games where set_key=? order by game_no", (set_key,)):
        side = "p1" if g["p1_player_id"] == pid else "p2" if g["p2_player_id"] == pid else None
        if not side:
            continue
        mr, league = parse_rank(g[side + "_rank"])
        mr = g[side + "_mr"] or mr
        if mr or league:
            return mr, league
    if pid == s["focus_player_id"] and s["focus_mr_start"]:
        return s["focus_mr_start"], None
    return None, None


def build(con, cfg):
    region = {r["player_id"]: r["region"] for r in con.execute("select player_id, region from players")}
    reads = {(r["set_key"], r["player_id"]): r for r in con.execute("select * from reads")}
    rows = []
    for s in con.execute("select * from sets order by played_date, set_key").fetchall():
        g1 = con.execute("select winner_player_id from games where set_key=? order by game_no limit 1", (s["set_key"],)).fetchone()
        for side, pid, opp, ch, och, gw, gl in (("focus", s["focus_player_id"], s["opp_player_id"], s["focus_char"], s["opp_char"], s["focus_games"], s["opp_games"]),
                                                ("opp", s["opp_player_id"], s["focus_player_id"], s["opp_char"], s["focus_char"], s["opp_games"], s["focus_games"])):
            mr, league = mr_at_set(con, s["set_key"], pid, s)
            bid, blabel = band_for(mr, league, region.get(pid))
            rd, ord_ = reads.get((s["set_key"], pid)), reads.get((s["set_key"], opp))
            rows.append(dict(set_key=s["set_key"], player_id=pid, opp_id=opp, played_date=s["played_date"], context=context_of(s),
                             format=s["format"], review=s["review"], character=ch, opp_character=och, games_won=gw, games_lost=gl,
                             won=int(s["winner_player_id"] == pid), mr=mr, league=league, band=bid, band_label=blabel,
                             weight=weight_for(mr, league, region.get(pid)),
                             archetype=rd["archetype"] if rd else None, lean=rd["lean"] if rd else None,
                             read_confidence=rd["confidence"] if rd else None, opp_archetype=ord_["archetype"] if ord_ else None,
                             lost_game1=int(bool(g1) and g1[0] is not None and g1[0] != pid), is_deviation=0))
    # deviation: archetype differs from the player's modal archetype (ties -> most recent)
    by = collections.defaultdict(list)
    for r in rows:
        if r["archetype"]:
            by[r["player_id"]].append(r)
    for pid, rs in by.items():
        cnt = collections.Counter(r["archetype"] for r in rs)
        top = max(cnt.values())
        modal = next(r["archetype"] for r in reversed(rs) if cnt[r["archetype"]] == top)
        for r in rs:
            r["is_deviation"] = int(r["archetype"] != modal)
    con.executemany("insert into player_set values (:set_key,:player_id,:opp_id,:played_date,:context,:format,:review,:character,:opp_character,"
                    ":games_won,:games_lost,:won,:mr,:league,:band,:band_label,:weight,:archetype,:lean,:read_confidence,:opp_archetype,"
                    ":lost_game1,:is_deviation)", rows)
    return len(rows)

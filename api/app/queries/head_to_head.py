from ..db import rows, one

METRICS = ["throws", "throw_techs", "anti_airs", "counter_hits", "punish_counters", "raw_drive_rush", "burnouts", "perfect_parries",
           "after_block_attack", "wake_up_attack", "drive_reversals"]


def per_game(pid, set_keys=None):
    """per-game rates for one player, over the given sets (or all)."""
    if set_keys is not None and not set_keys:
        return {}
    flt = "" if set_keys is None else f"and set_key in ({','.join(':k%d' % i for i in range(len(set_keys)))})"
    params = {"pid": pid, **({f"k{i}": k for i, k in enumerate(set_keys)} if set_keys else {})}
    r = rows(f"select metric, sum(value) as v from set_stats where player_id=:pid {flt} group by metric", **params)
    d = {x["metric"]: x["v"] for x in r}
    g = d.get("games") or 1
    return {m: round((d.get(m) or 0) / g, 2) for m in METRICS} | {"games": int(d.get("games") or 0)}


def h2h(a, b):
    pa, pb = one("select player_id, name from players where player_id=:a", a=a), one("select player_id, name from players where player_id=:b", b=b)
    if not pa or not pb:
        return None
    sets = rows("""select ss.*, case when ss.p1_id = ps.player_id then ss.game_scores else ss.game_scores_p2 end as a_game_scores, ps.won as a_won, ps.character as a_char, ps.opp_character as b_char,
                          ps.archetype as a_archetype, ps.opp_archetype as b_archetype, ps.games_won as a_games, ps.games_lost as b_games
                   from player_set ps join set_summary ss on ss.set_key=ps.set_key
                   where ps.player_id=:a and ps.opp_id=:b order by ps.played_date, (select min(g.played_time) from games g where g.set_key = ps.set_key), ps.set_key""", a=a, b=b)
    keys = [s["set_key"] for s in sets]
    def side(pid, arch_key):
        overall = one("select archetype, archetype_n, sets from player_profile where player_id=:p", p=pid) or {}
        here = {}
        for s in sets:
            here[s[arch_key]] = here.get(s[arch_key], 0) + 1
        return {"pairing": per_game(pid, keys), "overall": per_game(pid), "archetypes_here": here, "archetype_overall": overall.get("archetype")}
    return {
        "a": pa, "b": pb, "sets": sets,
        "record": {"sets": len(sets), "a_sets": sum(s["a_won"] or 0 for s in sets), "a_games": sum(s["a_games"] or 0 for s in sets),
                   "b_games": sum(s["b_games"] or 0 for s in sets),
                   "first": sets[0]["played_date"] if sets else None, "last": sets[-1]["played_date"] if sets else None},
        "sides": {"a": side(a, "a_archetype"), "b": side(b, "b_archetype")},
        "predictions": rows(f"select * from predictions where set_key in ({','.join(':k%d' % i for i in range(len(keys)))})", **{f"k{i}": k for i, k in enumerate(keys)}) if keys else [],
    }

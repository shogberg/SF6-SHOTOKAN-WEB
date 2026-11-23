"""What winning players do: compare the winner and the loser of the same set, stat by stat.

Pairing inside a set keeps the opponent, the matchup and the day the same, so a difference says more than comparing
all winners with all losers. Each pair is weighted by the mean MR weight of its two players (player_set.weight,
see docs/analysis-methods.md), so higher-MR sets count for more."""
from collections import defaultdict
from ..db import rows

PER_GAME = [  # (metric, label, group, lower_is_better)
    ("counter_hits", "Counter hits", "Offense", False),
    ("punish_counters", "Punish counters", "Offense", False),
    ("throws", "Throws landed", "Offense", False),
    ("combo_drive_rush_cancel", "Combo Drive Rush cancels (cashing in a hit)", "Offense", False),
    ("pressure_drive_rush_cancel", "Pressure Drive Rush cancels (on block)", "Drive", None),
    ("raw_drive_rush", "Raw Drive Rushes", "Drive", None),
    ("drive_reversals", "Drive Reversals", "Drive", None),
    ("burnouts", "Burnouts", "Drive", True),
    ("anti_airs", "Anti-airs", "Defense", False),
    ("throw_techs", "Throw techs", "Defense", False),
    ("perfect_parries", "Perfect parries", "Defense", False),
]
RATES = [  # (numerator, denominator, label, group)
    ("after_block_hold", "after_block_n", "Held block after blocking a string", "Defense"),
    ("after_block_attack_f0", "after_block_n", "Pressed on the first free frame after blocking", "Defense"),
    ("wake_up_hold", "wake_up_n", "Held block on wake-up", "Defense"),
    ("wake_up_attack", "wake_up_n", "Pressed a button on wake-up", "Defense"),
    ("wake_up_jump", "wake_up_n", "Jumped on wake-up", "Defense"),
    ("decision_presses", "press_rounds", "Decision presses per round", "Neutral"),
]
SITUATIONS = ["neutral", "pressure", "oki", "punish", "defense"]
HIGH_END = {"Temperament (defense)": "mindful", "Temperament (offense)": "mindful", "Adaptability": "elastic", "Risk tolerance": "high risk",
            "Initiative": "proactive", "Composure": "tilts", "Variety": "mixed", "Resource use": "spendthrift"}


def _pairs():
    sets = rows("""select s.set_key, s.focus_player_id as f, s.opp_player_id as o, s.winner_player_id as w,
                          coalesce(pf.weight, 1) as wf, coalesce(po.weight, 1) as wo
                   from sets s
                   left join player_set pf on pf.set_key = s.set_key and pf.player_id = s.focus_player_id
                   left join player_set po on po.set_key = s.set_key and po.player_id = s.opp_player_id
                   where s.winner_player_id is not null""")
    st = defaultdict(dict)
    for r in rows("select set_key, player_id, metric, value from set_stats"):
        st[(r["set_key"], r["player_id"])][r["metric"]] = r["value"] or 0
    sp = defaultdict(dict)
    for r in rows("select set_key, player_id, axis, score from spectra where score is not null"):
        sp[(r["set_key"], r["player_id"])][r["axis"]] = r["score"]
    out = []
    for s in sets:
        loser = s["o"] if s["w"] == s["f"] else s["f"]
        W, L = st.get((s["set_key"], s["w"])), st.get((s["set_key"], loser))
        if not W or not L or not W.get("games"):
            continue
        out.append(dict(set_key=s["set_key"], weight=(s["wf"] + s["wo"]) / 2, W=W, L=L, games=W["games"],
                        sW=sp.get((s["set_key"], s["w"]), {}), sL=sp.get((s["set_key"], loser), {})))
    return out


def _row(metric, label, group, vals, unit, better=None):
    """vals: [(winner, loser, weight)]"""
    vals = [v for v in vals if v[0] is not None and v[1] is not None]
    if not vals:
        return None
    tw = sum(w for _, _, w in vals) or 1
    mw = sum(a * w for a, _, w in vals) / tw
    ml = sum(b * w for _, b, w in vals) / tw
    dec = [v for v in vals if v[0] != v[1]]
    hi = sum(w for a, b, w in dec if a > b) / (sum(w for _, _, w in dec) or 1) if dec else None
    return dict(metric=metric, label=label, group=group, unit=unit, n=len(vals), ties=len(vals) - len(dec),
                winner=round(mw, 3), loser=round(ml, 3), diff=round(mw - ml, 3),
                winner_higher=None if hi is None else round(hi, 3), lower_is_better=better)


def traits():
    P = _pairs()
    out = []
    for m, label, group, better in PER_GAME:
        out.append(_row(m, label, group, [(p["W"].get(m, 0) / p["games"], p["L"].get(m, 0) / p["games"], p["weight"]) for p in P], "per game", better))
    for a, b, label, group in RATES:
        out.append(_row(a, label, group, [(p["W"].get(a, 0) / p["W"][b] if p["W"].get(b) else None,
                                           p["L"].get(a, 0) / p["L"][b] if p["L"].get(b) else None, p["weight"]) for p in P],
                        "per round" if b == "press_rounds" else "share"))
    for s in SITUATIONS:
        k = f"taken_situation_share: {s}"
        out.append(_row(k, f"Damage taken in {s}", "Damage taken", [(p["W"].get(k, 0), p["L"].get(k, 0), p["weight"]) for p in P], "share", True))
    axes = sorted({a for p in P for a in p["sW"]} | {a for p in P for a in p["sL"]})
    for ax in axes:
        out.append(_row(f"spectrum: {ax}", f"{ax} (higher = {HIGH_END[ax]})" if ax in HIGH_END else ax, "Spectra", [(p["sW"].get(ax), p["sL"].get(ax), p["weight"]) for p in P], "score 1-5"))
    out = [r for r in out if r]
    arch = rows("""select archetype, count(*) as n, sum(won) as wins, sum(weight) as w, sum(won * weight) as ww
                   from player_set where archetype is not null and won is not null group by archetype order by n desc""")
    for a in arch:
        a["win_rate"] = round(a["wins"] / a["n"], 3) if a["n"] else None
        w, ww = a.pop("w"), a.pop("ww")
        a["weighted_win_rate"] = round(ww / w, 3) if w else None
    return dict(pairs=len(P), rows=out, archetypes=arch)

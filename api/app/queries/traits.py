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
            "Initiative": "proactive", "Composure": "tilts", "Variety": "mixed", "Resource use": "spendthrift",
            "Cash-in": "cashes in", "Space": "takes ground"}


def me_id():
    """The configured player (settings 'me' in the snapshot), or None."""
    r = rows("select p.player_id from settings s join players p on p.name = s.value where s.key = 'me'")
    if not r:
        r = rows("select n.player_id from settings s join player_names n on n.name = s.value where s.key = 'me'")
    return r[0]["player_id"] if r else None


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
        out.append(dict(set_key=s["set_key"], weight=(s["wf"] + s["wo"]) / 2, W=W, L=L, games=W["games"], w=s["w"], l=loser,
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


def traits(view="all"):
    """view: 'all' (every decided set), 'others' (sets without the configured player) or 'me' (the configured
    player's own won sets against their lost sets)."""
    me = me_id()
    if view == "me":
        return _my_traits(me)
    P = _pairs()
    if view == "others" and me is not None:
        P = [p for p in P if me not in (p["w"], p["l"])]
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
    return dict(view=view, me=me, pairs=len(P), rows=out, archetypes=arch)


def _my_traits(me):
    """The configured player's stats in the sets they won against the sets they lost (not paired: each side is the
    MR-weighted mean over those sets). 'winner' / 'loser' hold the won-sets / lost-sets means; winner_higher is None."""
    if me is None:
        return dict(view="me", me=None, pairs=0, won=0, lost=0, rows=[], archetypes=[])
    sets = rows("""select s.set_key, s.winner_player_id = :me as won, coalesce(ps.weight, 1) as w
                   from sets s left join player_set ps on ps.set_key = s.set_key and ps.player_id = :me
                   where s.winner_player_id is not null and :me in (s.focus_player_id, s.opp_player_id)""", me=me)
    st = defaultdict(dict)
    for r in rows("select set_key, metric, value from set_stats where player_id = :me", me=me):
        st[r["set_key"]][r["metric"]] = r["value"] or 0
    sp = defaultdict(dict)
    for r in rows("select set_key, axis, score from spectra where player_id = :me and score is not null", me=me):
        sp[r["set_key"]][r["axis"]] = r["score"]
    S = [dict(s, W=st.get(s["set_key"], {}), sW=sp.get(s["set_key"], {})) for s in sets if st.get(s["set_key"], {}).get("games")]
    won, lost = [s for s in S if s["won"]], [s for s in S if not s["won"]]

    def mean(group, f):
        v = [(f(s), s["w"]) for s in group]
        v = [x for x in v if x[0] is not None]
        tw = sum(w for _, w in v)
        return (sum(a * w for a, w in v) / tw if tw else None), len(v)

    def row(metric, label, group, f, unit, better=None):
        a, na = mean(won, f)
        b, nb = mean(lost, f)
        if a is None or b is None:
            return None
        return dict(metric=metric, label=label, group=group, unit=unit, n=na + nb, ties=0, n_won=na, n_lost=nb,
                    winner=round(a, 3), loser=round(b, 3), diff=round(a - b, 3), winner_higher=None, lower_is_better=better)

    out = []
    for m, label, group, better in PER_GAME:
        out.append(row(m, label, group, lambda s, m=m: s["W"].get(m, 0) / s["W"]["games"], "per game", better))
    for a_, b_, label, group in RATES:
        out.append(row(a_, label, group, lambda s, a_=a_, b_=b_: (s["W"].get(a_, 0) / s["W"][b_]) if s["W"].get(b_) else None,
                       "per round" if b_ == "press_rounds" else "share"))
    for sit in SITUATIONS:
        k = f"taken_situation_share: {sit}"
        out.append(row(k, f"Damage taken in {sit}", "Damage taken", lambda s, k=k: s["W"].get(k, 0), "share", True))
    for ax in sorted({a for s in S for a in s["sW"]}):
        out.append(row(f"spectrum: {ax}", f"{ax} (higher = {HIGH_END[ax]})" if ax in HIGH_END else ax, "Spectra",
                       lambda s, ax=ax: s["sW"].get(ax), "score 1-5"))
    return dict(view="me", me=me, pairs=len(S), won=len(won), lost=len(lost), rows=[r for r in out if r], archetypes=[])

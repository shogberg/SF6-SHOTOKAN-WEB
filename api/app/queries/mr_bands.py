"""MR bands: how players differ by skill band (docs/pages/mr-bands.md).

The unit is a player-set: one player in one reviewed set, banded by their MR at that set (player_set.band, set at
publish from docs/analysis-methods.md). Per-game and per-round numbers are that player's rates in that set; a band's
value is the mean over its player-sets, with the median and n alongside. MR unknown player-sets are left out and
counted. `view=others` leaves out the configured player (settings 'me'), whose sets are most of the data."""
import json
from collections import defaultdict
from statistics import mean, median, pstdev
from ..db import rows, meta_value
from .traits import me_id, HIGH_END

# (key, label, group, kind, source): kind per_game / per_round / rate / value; source = metric or (num, den)
METRICS = [
    ("decision_presses_pr", "Decision presses per round", "Button economy", "value", None),
    ("dmg_per_press", "Damage per decision press", "Button economy", "value", None),
    ("press_share", "Share of the set's decision presses (%)", "Button economy", "value", None),
    ("damage_dealt_pr", "Damage dealt per round", "Button economy", "value", None),
    ("raw_drive_rush", "Raw Drive Rushes", "Drive economy", "per_game", "raw_drive_rush"),
    ("pressure_drive_rush_cancel", "Pressure Drive Rush cancels (on block)", "Drive economy", "per_game", "pressure_drive_rush_cancel"),
    ("combo_drive_rush_cancel", "Combo Drive Rush cancels (on hit)", "Drive economy", "per_game", "combo_drive_rush_cancel"),
    ("drive_reversals", "Drive Reversals", "Drive economy", "per_game", "drive_reversals"),
    ("burnouts", "Burnouts", "Drive economy", "per_game", "burnouts"),
    ("drive_spent_pr", "Drive bars spent per round", "Drive economy", "value", None),
    ("od_pr", "Drive bars on OD specials per round", "Drive economy", "value", None),
    ("drive_lost_block_pr", "Drive bars lost blocking per round", "Drive economy", "value", None),
    ("drive_gain_block_pr", "Drive bars gained on the opponent's block per round", "Drive economy", "value", None),
    ("super_pr", "Super bars spent per round", "Drive economy", "value", None),
    ("lost_round_full_super", "Lost rounds ended with 3 super bars (%)", "Drive economy", "value", None),
    ("throws", "Throws landed", "Offense, pressure and oki", "per_game", "throws"),
    ("counter_hits", "Counter hits", "Offense, pressure and oki", "per_game", "counter_hits"),
    ("punish_counters", "Punish counters", "Offense, pressure and oki", "per_game", "punish_counters"),
    ("dealt_neutral", "Damage dealt in neutral (%)", "Offense, pressure and oki", "value", None),
    ("dealt_pressure", "Damage dealt in pressure (%)", "Offense, pressure and oki", "value", None),
    ("dealt_oki", "Damage dealt on oki (%)", "Offense, pressure and oki", "value", None),
    ("dealt_punish", "Damage dealt from punishes (%)", "Offense, pressure and oki", "value", None),
    ("anti_airs", "Anti-airs", "Defense", "per_game", "anti_airs"),
    ("throw_techs", "Throw techs", "Defense", "per_game", "throw_techs"),
    ("perfect_parries", "Perfect parries", "Defense", "per_game", "perfect_parries"),
    ("after_block_hold", "Held block after blocking a string (%)", "Defense", "rate", ("after_block_hold", "after_block_n")),
    ("after_block_attack_f0", "Pressed on the first free frame after blocking (%)", "Defense", "rate", ("after_block_attack_f0", "after_block_n")),
    ("wake_up_hold", "Held block on wake-up (%)", "Defense", "rate", ("wake_up_hold", "wake_up_n")),
    ("wake_up_attack", "Pressed a button on wake-up (%)", "Defense", "rate", ("wake_up_attack", "wake_up_n")),
    ("punish_close", "Close punish windows punished (%)", "Defense", "rate", ("punishes_landed_close", "punish_windows_close")),
    ("anti_air_rate", "Jump-ins anti-aired, when free to (%)", "Defense", "rate", ("jump_ins_anti_aired", "jump_ins_free")),
    ("jump_in_stopped", "Jump-ins stopped (anti-air, parry or landing punish), when free to (%)", "Defense", "rate", ("jump_ins_stopped", "jump_ins_free")),
    ("jump_ins_hit", "Jump-ins that hit while free to anti-air", "Defense", "per_game", "jump_ins_hit"),
    ("jump_ins_blocked", "Jump-ins blocked while free to anti-air", "Defense", "per_game", "jump_ins_blocked"),
    ("whiff_punish_rate", "Whiff-punish chances taken (%)", "Neutral", "rate", ("whiff_punishes", "whiff_chances")),
    ("whiffs_punished", "Own whiffs punished", "Neutral", "per_game", "whiffs_punished"),
    ("damage_taken_pr", "Damage taken per round", "Defense", "value", None),
]
LENSES = ["Counter-hit at mid range", "Walked in", "Jumped in on (no anti-air)", "Jumped", "Blocking, opened up", "Challenging pressure",
          "Challenging okizeme", "Pressed after turn ended", "Own offense beaten by a reversal", "Unsafe move punished", "Drive Rush / Impact checked",
          "Whiff punished"]
SMALL = 15   # fewer player-sets than this: the page dims the band
CONTEXTS = ("ranked", "other", "all")   # ranked sets / everything else (casual, custom room, local, tournament, unknown) / both


def context_ok(ctx, want):
    """player_set.context against a filter value: 'ranked', 'other' (not ranked) or 'all'."""
    if want in (None, "", "all"):
        return True
    return (ctx == "ranked") == (want == "ranked")


def _bands():
    b = json.loads(meta_value("bands") or "[]")
    order = [x for x in b if x["id"] == "diamond_below"] + [x for x in b if x["id"] not in ("diamond_below", "unknown")]
    return order


def _stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return {"mean": round(mean(vals), 2), "median": round(median(vals), 2), "n": len(vals)}


def mr_bands(view="all", context="all"):
    bands = _bands()
    ids = [b["id"] for b in bands]
    me = me_id() if view == "others" else None
    ps = rows("select set_key, player_id, opp_id, band, archetype, won, context from player_set")
    ps = [p for p in ps if context_ok(p["context"], context)]
    unknown = sum(1 for p in ps if p["band"] == "unknown")
    ps = [p for p in ps if p["band"] in ids and (me is None or p["player_id"] != me)]
    st = defaultdict(dict)
    for r in rows("select set_key, player_id, metric, value from set_stats"):
        st[(r["set_key"], r["player_id"])][r["metric"]] = r["value"] or 0
    res = defaultdict(lambda: defaultdict(float))
    rounds = defaultdict(int)
    lost_full = defaultdict(lambda: [0, 0])
    for r in rows("select set_key, player_id, drive_total, od_specials, loss_block, gain_block, super_bars from resources"):
        k = (r["set_key"], r["player_id"])
        a = res[k]
        a["drive"] += r["drive_total"] or 0; a["od"] += r["od_specials"] or 0; a["loss_block"] += r["loss_block"] or 0
        a["gain_block"] += r["gain_block"] or 0; a["super"] += r["super_bars"] or 0
        rounds[k] += 1
    # damage dealt by situation
    sit = defaultdict(lambda: defaultdict(float))
    for r in rows("select set_key, attacker_id, situation, sum(damage) as d from hits group by set_key, attacker_id, situation"):
        sit[(r["set_key"], r["attacker_id"])][r["situation"] or "other"] += r["d"] or 0
    # lost rounds with full super: the round's loser is taken as the player who took its last hit (a time-out or chip
    # finish can miss), and resources.super_end says what they had left
    last_hit = {}
    for r in rows("""select h.replay_id, h.round, h.victim_id from hits h
                     join (select replay_id, round, max(hit_id) as m from hits group by replay_id, round) x
                       on x.replay_id = h.replay_id and x.round = h.round and x.m = h.hit_id"""):
        last_hit[(r["replay_id"], r["round"])] = r["victim_id"]
    for r in rows("select set_key, player_id, replay_id, round, super_end from resources"):
        loser = last_hit.get((r["replay_id"], r["round"]))
        if loser == r["player_id"]:
            lf = lost_full[(r["set_key"], r["player_id"])]
            lf[1] += 1; lf[0] += 1 if (r["super_end"] or 0) >= 2.95 else 0

    def values(p):
        k = (p["set_key"], p["player_id"])
        s = st.get(k, {})
        o = st.get((p["set_key"], p["opp_id"]), {})
        g = s.get("games") or 1
        v = {}
        dp, pr = s.get("decision_presses"), s.get("press_rounds")
        v["decision_presses_pr"] = dp / pr if dp and pr else None
        v["dmg_per_press"] = s.get("damage_dealt", 0) / dp if dp else None
        v["press_share"] = 100 * dp / (dp + o.get("decision_presses", 0)) if dp and (dp + o.get("decision_presses", 0)) else None
        n = rounds.get(k)
        v["damage_dealt_pr"] = s.get("damage_dealt") / n if n and "damage_dealt" in s else None
        v["damage_taken_pr"] = s.get("damage_taken") / n if n and "damage_taken" in s else None
        a = res.get(k)
        if n and a is not None:
            v["drive_spent_pr"] = a["drive"] / n; v["od_pr"] = a["od"] / n
            v["drive_lost_block_pr"] = a["loss_block"] / n; v["drive_gain_block_pr"] = a["gain_block"] / n; v["super_pr"] = a["super"] / n
        lf = lost_full.get(k)
        v["lost_round_full_super"] = 100 * lf[0] / lf[1] if lf and lf[1] else None
        sd = sit.get(k)
        tot = sum(sd.values()) if sd else 0
        for x in ("neutral", "pressure", "oki", "punish"):
            v[f"dealt_{x}"] = 100 * sd.get(x, 0) / tot if tot else None
        for key, _l, _g, kind, src in METRICS:
            if kind == "per_game" and s:
                v[key] = s.get(src, 0) / g
            elif kind == "rate" and s:
                num, den = src
                v[key] = 100 * s.get(num, 0) / s[den] if s.get(den) else None
        has_lens = any(m.startswith("taken_share: ") for m in s)   # lenses are only computed for the reviewed (focus) player
        for lens in LENSES:
            v[f"lens:{lens}"] = 100 * s.get(f"taken_share: {lens}", 0) if has_lens else None
        return v

    by_band = defaultdict(list)
    for p in ps:
        by_band[p["band"]].append((p, values(p)))

    def table(keys):
        out = []
        for key, label, group in keys:
            row = {"key": key, "label": label, "group": group, "bands": {}}
            for b in ids:
                row["bands"][b] = _stats([v.get(key) for _p, v in by_band.get(b, [])])
            out.append(row)
        return out

    metrics = table([(k, l, g) for k, l, g, _kind, _s in METRICS])
    lenses = table([(f"lens:{x}", x, "Damage taken (% of damage taken)") for x in LENSES])

    spec = defaultdict(lambda: defaultdict(list))
    keyset = {(p["set_key"], p["player_id"]): p["band"] for p in ps}
    for r in rows("select set_key, player_id, axis, score from spectra"):
        b = keyset.get((r["set_key"], r["player_id"]))
        if b and r["score"] is not None:
            spec[r["axis"]][b].append(r["score"])
    spectra = [{"key": f"spectrum:{ax}", "label": ax, "high_end": HIGH_END.get(ax), "group": "Spectra",
                "bands": {b: _stats(spec[ax].get(b, [])) for b in ids}} for ax in HIGH_END]

    arche = {}
    for b in ids:
        c = defaultdict(int)
        for p, _v in by_band.get(b, []):
            c[(p["archetype"] or "Unread").split()[0]] += 1
        tot = sum(c.values())
        wins = defaultdict(lambda: [0, 0])
        for p, _v in by_band.get(b, []):
            a = (p["archetype"] or "Unread").split()[0]
            if p["won"] is not None:
                wins[a][1] += 1; wins[a][0] += 1 if p["won"] else 0
        arche[b] = [{"archetype": a, "n": n, "pct": round(100 * n / tot) if tot else None,
                     "win_pct": round(100 * wins[a][0] / wins[a][1]) if wins[a][1] else None} for a, n in sorted(c.items(), key=lambda x: -x[1])]

    # biggest differences between neighbouring bands (both with SMALL+ player-sets), in units of the metric's spread
    diffs = []
    allrows = metrics + spectra
    for r in allrows:
        allv = [v.get(r["key"]) for b in ids for _p, v in by_band.get(b, [])] if not r["key"].startswith("spectrum:") else \
            [x for b in ids for x in spec[r["label"]].get(b, [])]
        allv = [x for x in allv if x is not None]
        sd = pstdev(allv) if len(allv) > 2 else 0
        if not sd:
            continue
        for a, b in zip(ids, ids[1:]):
            x, y = r["bands"].get(a), r["bands"].get(b)
            if x and y and x["n"] >= SMALL and y["n"] >= SMALL:
                diffs.append({"key": r["key"], "label": r["label"], "group": r["group"], "from": a, "to": b,
                              "from_mean": x["mean"], "to_mean": y["mean"], "effect": round((y["mean"] - x["mean"]) / sd, 2),
                              "n_from": x["n"], "n_to": y["n"]})
    diffs.sort(key=lambda d: -abs(d["effect"]))

    return {"bands": [{**b, "player_sets": len(by_band.get(b["id"], [])),
                       "players": len({p["player_id"] for p, _v in by_band.get(b["id"], [])})} for b in bands],
            "unknown_left_out": unknown, "small": SMALL, "view": view, "context": context or "all",
            "metrics": metrics, "lenses": lenses, "spectra": spectra, "archetypes": arche, "biggest_differences": diffs[:12]}

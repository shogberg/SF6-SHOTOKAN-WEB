from ..db import rows, one
from ..util import loads

PROFILE_JSON = ("characters", "reviews_json", "spectra_json", "per_game_json", "opp_did_json")


def search(q, limit=20):
    like = f"%{q.strip().lower()}%"
    return rows("""
        select p.player_id, p.name, p.cfn_id, p.sets, p.latest_band_label, p.characters,
               (select group_concat(distinct n.name) from player_names n where n.player_id=p.player_id and lower(n.name)<>lower(p.name)) as other_names
        from player_profile p
        where lower(p.name) like :like or p.cfn_id = :exact
           or p.player_id in (select player_id from player_names where lower(name) like :like)
        order by (lower(p.name) = :exactl) desc, p.sets desc, p.name limit :limit""",
                like=like, exact=q.strip(), exactl=q.strip().lower(), limit=limit)


def list_all():
    return rows("""select player_id, name, cfn_id, sets, sets_won, games_won, games_lost, characters, latest_mr, latest_league,
                          latest_band_label, archetype, last_date
                   from player_profile order by lower(name)""")


def profile(pid):
    p = one("select * from player_profile where player_id=:pid", pid=pid)
    if not p:
        return None
    for k in PROFILE_JSON:
        p[k.replace("_json", "")] = loads(p.pop(k), [] if k == "characters" else {})
    p["other_names"] = [r["name"] for r in rows("select distinct name from player_names where player_id=:pid and lower(name)<>lower(:n)", pid=pid, n=p["name"])]
    try:   # snapshots before schema 1.2 have no player_character table
        p["by_character"] = rows("""select character, sets, sets_won, games, games_won, games_lost, per_game_json, spectra_json, stats_source
                                    from player_character where player_id=:pid order by games desc, character""", pid=pid)
    except Exception:
        p["by_character"] = []
    for c in p["by_character"]:
        c["per_game"] = loads(c.pop("per_game_json"), {}); c["spectra"] = loads(c.pop("spectra_json"), [])
    p["top_opponents"] = rows("""select ps.opp_id as player_id, pp.name, count(*) as sets, sum(ps.won) as wins
        from player_set ps join players pp on pp.player_id=ps.opp_id where ps.player_id=:pid
        group by ps.opp_id order by sets desc, pp.name limit 8""", pid=pid)
    return p


def archetypes(pid):
    return {
        "summary": rows("select archetype, sets, wins, losses from player_archetype_summary where player_id=:pid order by sets desc", pid=pid),
        "spectra_by_result": rows("select axis, mean_win, n_win, mean_loss, n_loss, mean_all, sd_all from player_spectra_by_result where player_id=:pid", pid=pid),
        "deviations": rows("select from_archetype, to_archetype, context, n from player_deviation where player_id=:pid order by n desc", pid=pid),
        "timeline": rows("""select ps.set_key, ps.played_date, ps.archetype, ps.lean, ps.read_confidence, ps.won, ps.is_deviation, ps.lost_game1,
                                   ps.character, ps.opp_archetype, ps.band_label, o.name as opponent
                            from player_set ps join players o on o.player_id=ps.opp_id
                            where ps.player_id=:pid order by ps.played_date, ps.set_key""", pid=pid),
    }


SET_FILTERS = {"opponent": "ps.opp_id = :opponent", "character": "ps.character = :character", "review": "ps.review = :review",
               "context": "ps.context = :context", "band": "ps.band = :band", "date_from": "ps.played_date >= :date_from",
               "date_to": "ps.played_date <= :date_to"}


def sets(pid, **f):
    where = ["ps.player_id = :pid"]
    params = {"pid": pid}
    for k, cond in SET_FILTERS.items():
        if f.get(k) not in (None, ""):
            where.append(cond); params[k] = f[k]
    if f.get("result") in ("won", "lost"):
        where.append("ps.won = :won"); params["won"] = 1 if f["result"] == "won" else 0
    return rows(f"""
        select ps.set_key, ps.played_date, ps.context, ps.format, ps.review, ps.character, ps.opp_character, ps.opp_id,
               o.name as opponent, ps.games_won, ps.games_lost, ps.won, ps.mr, ps.league, ps.band_label,
               opp.mr as opp_mr, opp.league as opp_league, opp.band_label as opp_band_label,
               ps.archetype, ps.read_confidence, case when ss.p1_id = ps.player_id then ss.game_scores else ss.game_scores_p2 end as game_scores, ss.has_prediction, ss.prediction_verdict, ss.prediction_correct
        from player_set ps
        join players o on o.player_id = ps.opp_id
        join set_summary ss on ss.set_key = ps.set_key
        left join player_set opp on opp.set_key = ps.set_key and opp.player_id = ps.opp_id
        where {' and '.join(where)}
        order by ps.played_date desc, ps.set_key desc""", **params)


def _mr_change(my_mr, opp_mr, won):
    """sfbuff's MR formula (Elo, K = 16): used when the snapshot has no stored change for a game (older sources)."""
    return round(16 * ((1 if won else 0) - 1 / (1 + 10 ** ((opp_mr - my_mr) / 400.0))))


def mr_history(pid, date_from=None, date_to=None, character=None):
    """The player's MR over time from reviewed ranked games: one point per game with the MR before it and after it.
    MR is per character, so each point carries its character. The change after a game is the tools' stored
    p1/p2_mr_change (observed from the next game in the set, or calculated for the last one) when the source has it,
    else sfbuff's formula. Games without an MR on both sides (below Master, unranked) are left out."""
    cols = {r["name"] for r in rows("select name from pragma_table_info('games')")}
    chg = ("case when g.p1_player_id = :pid then g.p1_mr_change else g.p2_mr_change end" if "p1_mr_change" in cols else "null")
    src = "g.mr_change_source" if "mr_change_source" in cols else "null"
    r = rows(f"""
        select g.replay_id, g.set_key, g.game_no, s.played_date, g.played_time,
               case when g.p1_player_id = :pid then g.p1_char else g.p2_char end as character,
               case when g.p1_player_id = :pid then g.p1_mr else g.p2_mr end as mr,
               case when g.p1_player_id = :pid then g.p2_mr else g.p1_mr end as opp_mr,
               case when g.p1_player_id = :pid then g.p2_player_id else g.p1_player_id end as opp_id,
               g.winner_player_id = :pid as won, {chg} as change, {src} as source
        from games g join sets s on s.set_key = g.set_key
        where s.ranked = 1 and (g.p1_player_id = :pid or g.p2_player_id = :pid)""", pid=pid)
    names = {x["player_id"]: x["name"] for x in rows("select player_id, name from players")}
    out = []
    for x in r:
        if not x["mr"] or not x["opp_mr"] or x["mr"] <= 0 or x["opp_mr"] <= 0:
            continue
        t = x["played_time"] or ""
        x["at"] = t if len(t) > 8 else f"{x['played_date']} {t or '00:00'}"
        if x["change"] is None:
            x["change"] = _mr_change(x["mr"], x["opp_mr"], x["won"]); x["source"] = "calculated"
        x["mr_after"] = x["mr"] + x["change"]
        x["opponent"] = names.get(x["opp_id"])
        x["won"] = bool(x["won"])
        out.append(x)
    out.sort(key=lambda x: (x["at"], x["set_key"], x["game_no"]))
    chars = sorted({x["character"] for x in out}, key=lambda c: min(i for i, y in enumerate(out) if y["character"] == c))
    if character:
        out = [x for x in out if x["character"] == character]
    if date_from:
        out = [x for x in out if x["at"][:10] >= date_from]
    if date_to:
        out = [x for x in out if x["at"][:10] <= date_to]
    return out, chars

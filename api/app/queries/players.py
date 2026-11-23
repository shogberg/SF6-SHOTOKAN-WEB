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

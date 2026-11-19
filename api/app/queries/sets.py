import json
from ..db import rows, one
from ..util import loads

DOCS = ("story", "story_games", "set_gameplan", "tournament", "findings", "fixes", "training", "punish", "habits", "archetypes")
# extra tournament write-ups from the other player's side are stored as "tournament_<player>"
is_doc = lambda name: name in DOCS or name.startswith("tournament_")


def detail(set_key):
    s = one("""select ss.*, a.name as p1_name, b.name as p2_name from set_summary ss
               join players a on a.player_id=ss.p1_id join players b on b.player_id=ss.p2_id where ss.set_key=:k""", k=set_key)
    if not s:
        return None
    k = set_key
    players = rows("""select ps.*, p.name from player_set ps join players p on p.player_id=ps.player_id where ps.set_key=:k""", k=k)
    for p in players:
        pid = p["player_id"]
        p["spectra"] = rows("select axis, score, label, evidence from spectra where set_key=:k and player_id=:pid", k=k, pid=pid)
        p["read"] = one("select archetype, lean, confidence, evidence, counter_note, risk_tolerance, temperament from reads where set_key=:k and player_id=:pid", k=k, pid=pid)
        p["habits"] = rows("select kind, area, habit, seen, times, fix, confidence, source from habits where set_key=:k and player_id=:pid order by habit_row", k=k, pid=pid)
        p["stats"] = {r["metric"]: r["value"] for r in rows("select metric, value from set_stats where set_key=:k and player_id=:pid", k=k, pid=pid)}
    docs = {r["dataset"]: loads(r["rows"], []) for r in rows("select dataset, rows from review_docs where set_key=:k", k=k) if is_doc(r["dataset"])}
    return {
        "summary": s,
        "games": rows("""select replay_id, game_no, played_time, p1_player_id, p2_player_id, p1_char, p2_char, p1_control, p2_control,
                                p1_mr, p2_mr, p1_rank, p2_rank, winner_player_id, round_score, round_winners
                         from games where set_key=:k order by game_no""", k=k),
        "players": players,
        "predictions": [dict(r, body=loads(r.pop("body_json"), {})) for r in rows("select * from predictions where set_key=:k order by idx", k=k)],
        "docs": docs,
        "hits": rows("select * from hits where set_key=:k order by replay_id, round, round_timer desc", k=k),
        "events": rows("select * from events where set_key=:k", k=k),
        "resources": rows("select * from resources where set_key=:k", k=k),
        "parries": rows("select * from parries where set_key=:k", k=k),
    }


def all_sets():
    """Every set, newest first (for browsing without a player)."""
    return rows("""select ss.set_key, ss.played_date, ss.context, ss.format, ss.review, ss.p1_id, ss.p2_id, a.name as p1_name, b.name as p2_name,
                          ss.p1_char, ss.p2_char, ss.p1_games, ss.p2_games, ss.winner_id, ss.game_scores,
                          ss.p1_mr, ss.p2_mr, ss.p1_league, ss.p2_league, ss.has_prediction, ss.prediction_correct
                   from set_summary ss join players a on a.player_id=ss.p1_id join players b on b.player_id=ss.p2_id
                   order by ss.played_date desc, ss.set_key desc""")


def recent(limit=12):
    return rows("""select ss.set_key, ss.played_date, ss.context, ss.review, ss.p1_id, ss.p2_id, a.name as p1_name, b.name as p2_name,
                          ss.p1_char, ss.p2_char, ss.p1_games, ss.p2_games, ss.winner_id
                   from set_summary ss join players a on a.player_id=ss.p1_id join players b on b.player_id=ss.p2_id
                   order by ss.played_date desc, ss.set_key desc limit :n""", n=limit)

"""set_summary (one row per set) and predictions (from review_docs 'prediction')."""
import json


def build(con, cfg):
    ps = {(r["set_key"], r["player_id"]): r for r in con.execute("select * from player_set")}
    n = 0
    preds = {}
    for r in con.execute("select set_key, rows from review_docs where dataset='prediction'"):
        try:
            items = json.loads(r["rows"]) or []
        except ValueError:
            items = []
        out = []
        for i, p in enumerate(items):
            v = p.get("verdict") or ""
            correct = 1 if v.lower().startswith("right") else 0 if v.lower().startswith("wrong") else None
            out.append((r["set_key"], i, p.get("written_at"), p.get("predicted"), p.get("actual"), v, correct, json.dumps(p, ensure_ascii=False)))
        con.executemany("insert into predictions values (?,?,?,?,?,?,?,?)", out)
        preds[r["set_key"]] = out
    for s in con.execute("select * from sets").fetchall():
        games = con.execute("select game_no, round_score, winner_player_id, p1_player_id from games where set_key=? order by game_no", (s["set_key"],)).fetchall()
        def oriented(g, pid):           # games.round_score is the game's P1 first; turn it to pid first
            rs = g["round_score"] or "?"
            if "-" not in rs or g["p1_player_id"] == pid: return rs
            x, y = rs.split("-", 1); return f"{y}-{x}"
        a, b = 0, 0; prog = []
        for g in games:
            if g["winner_player_id"] == s["focus_player_id"]: a += 1
            elif g["winner_player_id"] == s["opp_player_id"]: b += 1
            prog.append(f"{a}-{b}")
        f, o = ps.get((s["set_key"], s["focus_player_id"])), ps.get((s["set_key"], s["opp_player_id"]))
        pr = preds.get(s["set_key"]) or []
        note = s["note"] if s["note"] and "dashboard" not in s["note"].lower() else None
        con.execute("insert into set_summary values (?,?,?,?,?,?, ?,?,?,?,?,?,?, ?,?,?,?, ?,?,?,?,?,?, ?,?, ?,?,?)", (
            s["set_key"], s["played_date"], f["context"] if f else None, s["format"], s["review"], note,
            s["focus_player_id"], s["opp_player_id"], s["focus_char"], s["opp_char"], s["focus_games"], s["opp_games"], s["winner_player_id"],
            ", ".join(oriented(g, s["focus_player_id"]) for g in games), ", ".join(oriented(g, s["opp_player_id"]) for g in games), ", ".join(prog), len(games),
            f["mr"] if f else None, o["mr"] if o else None, f["league"] if f else None, o["league"] if o else None,
            f["band_label"] if f else None, o["band_label"] if o else None,
            f["archetype"] if f else None, o["archetype"] if o else None,
            int(bool(pr)), pr[0][5] if pr else None, pr[0][6] if pr else None))
        n += 1
    return n

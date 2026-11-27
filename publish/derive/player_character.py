"""player_character: each player's record, per-game stats and spectra split by the character they played.

Per-game stats come from game_stats (one row per game, with that game's character), so a mid-set character switch
is split correctly. Sets ingested before game_stats existed fall back to their whole-set stats, counted under the
set's character (stats_source 'sets'). Spectra are per set, so they go to the set's character."""
import collections, json, statistics
from common import AXES, ENDS, spectrum_label

PG = ("throws", "throw_techs", "anti_airs", "counter_hits", "punish_counters", "raw_drive_rush", "burnouts", "perfect_parries")


def _has(con, table):
    return bool(con.execute("select 1 from sqlite_master where type='table' and name=?", (table,)).fetchone())


def build(con, cfg):
    has_gs = _has(con, "game_stats")
    games = con.execute("select replay_id, set_key, p1_player_id, p2_player_id, p1_char, p2_char, winner_player_id from games").fetchall()
    # games played and won per (player, character)
    g_n, g_w = collections.Counter(), collections.Counter()
    for g in games:
        for pid, ch in ((g["p1_player_id"], g["p1_char"]), (g["p2_player_id"], g["p2_char"])):
            if pid is None or not ch:
                continue
            g_n[(pid, ch)] += 1
            g_w[(pid, ch)] += int(g["winner_player_id"] == pid)
    # per-game stats: game_stats where present, else the whole set's stats under the set's character
    st = collections.defaultdict(lambda: collections.defaultdict(float)); st_games = collections.Counter(); src = {}
    covered = set()
    if has_gs:
        for r in con.execute("select set_key, replay_id, player_id, character, metric, value from game_stats"):
            covered.add((r["set_key"], r["player_id"]))
            key = (r["player_id"], r["character"])
            if r["metric"] == "games":
                st_games[key] += r["value"] or 0
            elif not r["metric"].startswith("taken_"):
                st[key][r["metric"]] += r["value"] or 0
            src.setdefault(key, "games")
    ps = con.execute("select set_key, player_id, character, won from player_set").fetchall()
    for s in ps:
        if (s["set_key"], s["player_id"]) in covered or not s["character"]:
            continue
        key = (s["player_id"], s["character"])
        for r in con.execute("select metric, value from set_stats where set_key=? and player_id=?", (s["set_key"], s["player_id"])):
            if r["metric"] == "games":
                st_games[key] += r["value"] or 0
            elif not r["metric"].startswith("taken_"):
                st[key][r["metric"]] += r["value"] or 0
        src[key] = "sets" if src.get(key) is None else ("mixed" if src[key] == "games" else src[key])
    # sets and spectra under the set's character
    sets_n, sets_w = collections.Counter(), collections.Counter(); sp = collections.defaultdict(lambda: collections.defaultdict(list))
    for s in ps:
        if not s["character"]:
            continue
        key = (s["player_id"], s["character"])
        sets_n[key] += 1; sets_w[key] += int(s["won"] or 0)
    for r in con.execute("""select sp.player_id, ps.character, sp.axis, sp.score from spectra sp
                            join player_set ps on ps.set_key = sp.set_key and ps.player_id = sp.player_id where sp.score is not null"""):
        sp[(r["player_id"], r["character"])][r["axis"]].append(r["score"])
    keys = set(g_n) | set(sets_n)
    n = 0
    for key in sorted(keys, key=lambda k: (k[0], -g_n[k])):
        pid, ch = key
        m, gms = st[key], st_games[key] or g_n[key] or 1
        pg = {k: round(m.get(k, 0) / gms, 1) for k in PG}
        pct = lambda a, b: round(100 * m.get(a, 0) / m[b]) if m.get(b) else None
        pg.update(after_block_attack_pct=pct("after_block_attack", "after_block_n"), wake_up_attack_pct=pct("wake_up_attack", "wake_up_n"),
                  anti_air_pct=pct("jump_ins_anti_aired", "jump_ins_free"), jump_ins_free=int(m.get("jump_ins_free", 0)),
                  whiff_punish_pct=pct("whiff_punishes", "whiff_chances"), whiff_chances=int(m.get("whiff_chances", 0)), games=int(gms))
        spectra = []
        for a in AXES:
            v = sp[key].get(a) or []
            if v:
                mean = statistics.mean(v); sc = int(round(mean))
                spectra.append(dict(axis=a, left=ENDS[a][0], right=ENDS[a][1], score=sc, label=spectrum_label(a, sc), mean=round(mean, 2), n=len(v),
                                    evidence=f"mean of {len(v)} set{'s' if len(v) != 1 else ''} on {ch}"))
            else:
                spectra.append(dict(axis=a, left=ENDS[a][0], right=ENDS[a][1], score=None, label=None, n=0, evidence="not enough data"))
        con.execute("insert into player_character values (?,?,?,?,?,?,?,?,?,?)",
                    (pid, ch, sets_n[key], sets_w[key], g_n[key], g_w[key], g_n[key] - g_w[key], json.dumps(pg), json.dumps(spectra), src.get(key)))
        n += 1
    return n

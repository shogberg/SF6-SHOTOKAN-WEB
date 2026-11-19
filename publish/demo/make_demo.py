"""Make a synthetic source database in the sf6.db layout: made-up players, sets and stats.

  python make_demo.py demo_source.db [--seed 7]

Used by the tests, CI and `docker run ... --demo`. Contains no real player data."""
import json, random, sqlite3, sys

NAMES = ["Ryuko", "Bluefox", "Okidoki", "Footsie_Fan", "Pokemaster", "WakeupDP", "ShimmyKing", "Parrypal", "DriveRusher", "Zoneout"]
CHARS = ["Cammy", "Ryu", "Ken", "Guile", "Juri", "Mai", "Blanka", "JP", "Luke", "Marisa"]
ARCH = ["Aggressive", "Defensive", "Fundamentalist", "Balanced"]
AXES = ["Temperament (defense)", "Temperament (offense)", "Adaptability", "Risk tolerance", "Initiative", "Composure", "Variety", "Resource use"]
LABEL = {1: "Very", 2: "Leans", 3: "Middle", 4: "Leans", 5: "Very"}
METRICS = ["throws", "throw_techs", "anti_airs", "counter_hits", "punish_counters", "raw_drive_rush", "burnouts", "perfect_parries",
           "after_block_attack", "after_block_n", "wake_up_attack", "wake_up_n", "drive_reversals"]
LENSES = ["Pressed at mid range", "Walked in", "Jumped", "Blocking, opened up", "Pressed in their pressure / on wake-up", "Unsafe move punished"]
HABITS = [("Strength", "Offense", "Throws landed"), ("Strength", "Neutral", "Anti-airs on reaction"), ("Strength", "Offense", "Counter hits in pressure"),
          ("Leak", "Neutral", "Buttons at mid range got beaten"), ("Leak", "Defense", "Pressing after blocked strings"), ("Leak", "Drive", "Burns out and loses the round"),
          ("Leak", "Neutral", "Jumps into anti-airs")]

DDL = """
create table players (player_id integer primary key, cfn_id text, name text, first_seen text, last_seen text);
create table player_names (player_id integer, name text, first_seen text, last_seen text);
create table settings (key text primary key, value text);
create table sets (set_key text primary key, played_date text, ranked integer, format text, review text, focus_player_id integer, opp_player_id integer,
  focus_char text, opp_char text, focus_games integer, opp_games integer, winner_player_id integer, focus_mr_start integer, games_missing integer, note text,
  dashboard text, analyzer text, ingested_at text);
create table games (replay_id text, set_key text, game_no integer, played_time text, p1_player_id integer, p2_player_id integer, p1_char text, p2_char text,
  p1_control text, p2_control text, p1_mr integer, p2_mr integer, winner_player_id integer, round_score text, round_winners text, capture_file text,
  p1_lp integer, p2_lp integer, p1_rank text, p2_rank text);
create table hits (hit_id text, set_key text, replay_id text, round integer, round_timer integer, attacker_id integer, victim_id integer, attacker_char text,
  victim_char text, damage integer, starter text, hits_in_combo integer, hit_kind text, anti_air integer, situation text, lens text, victim_state text,
  victim_move text, note text, drive_spent real, super_spent real, drive_gained real, drive_damage real, knockdown text, kd_adv integer, corner_dist real, victim_drive_after real);
create table events (event_id text, set_key text, replay_id text, round integer, round_timer integer, player_id integer, type text, note text);
create table resources (set_key text, replay_id text, round integer, player_id integer, drive_rush real, drive_parry real, drive_impact real, drive_reversal real,
  od_specials real, drive_other real, drive_total real, super_bars real, supers text, burnouts integer, drive_end real, super_end real, gain_hit real, gain_block real,
  parry_regain real, loss_block real, loss_hit real, loss_hit_drive_impact real, loss_hit_punish_counter real, drive_rush_cancel real);
create table parries (set_key text, replay_id text, round integer, round_timer integer, player_id integer, frames integer, drive_before real, cost real,
  hits_parried integer, regained real, net real, perfect integer, next text);
create table timings (timing_id text, set_key text, replay_id text, round integer, round_timer integer, player_id integer, event text, action text, frames_until integer);
create table set_stats (set_key text, player_id integer, metric text, value real);
create table reads (set_key text, player_id integer, character text, archetype text, lean text, confidence text, evidence text, counter_note text,
  risk_tolerance text, temperament text, source text);
create table spectra (set_key text, player_id integer, axis text, score integer, label text, evidence text);
create table habits (habit_row integer primary key, set_key text, player_id integer, kind text, area text, habit text, seen text, times integer, fix text,
  confidence text, source text);
create table usage (set_key text, replay_id text, player_id integer, move text, n integer);
create table review_docs (set_key text, dataset text, rows text, updated text);
"""


def main(out, seed=7):
    R = random.Random(seed)
    con = sqlite3.connect(out); con.executescript("".join(f"drop table if exists {t};" for t in
        "players player_names settings sets games hits events resources parries timings set_stats reads spectra habits usage review_docs".split()) + DDL)
    con.execute("insert into settings values ('me', ?)", (NAMES[0],))
    base = {}
    for i, n in enumerate(NAMES, 1):
        con.execute("insert into players values (?,?,?,?,?)", (i, None, n, "2026-10-01", "2026-11-15"))
        con.execute("insert into player_names values (?,?,?,?)", (i, n, "2026-10-01", "2026-11-15"))
        base[i] = dict(char=CHARS[i - 1], mr=None if i in (9, 10) else R.choice([1350, 1480, 1550, 1650, 1720, 1850, 1950, 2050]),
                       league="Diamond" if i in (9, 10) else None, arch=R.choice(ARCH), spec={a: R.randint(1, 5) for a in AXES})
    hrow = 0
    for k in range(40):
        a = 1 if k % 2 == 0 else R.randint(2, 10)
        b = R.choice([x for x in range(1, 11) if x != a])
        pa, pb = base[a], base[b]
        skill = lambda p: (p["mr"] or 1300) + R.randint(-150, 150)
        n_games = 2 if R.random() < 0.5 else 3
        wins = [a if skill(pa) >= skill(pb) else b for _ in range(n_games)]
        if n_games == 2 and wins[0] != wins[1]: wins.append(wins[0])
        ga, gb = wins.count(a), wins.count(b)
        if ga == gb: wins[-1] = a; ga, gb = wins.count(a), wins.count(b)
        if max(ga, gb) > 2:  # keep FT2
            wins = wins[:3]; ga, gb = min(ga, 2), min(gb, 2)
        winner = a if ga > gb else b
        ids = [f"D{k:03d}G{g}" for g in range(1, len(wins) + 1)]
        key = "_".join(ids); date = f"2026-{10 + k // 25:02d}-{1 + k % 25:02d}"
        review = "Quick" if k % 5 else "Full"
        con.execute("insert into sets values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (key, date, 1, "FT2", review, a, b, pa["char"], pb["char"], ga, gb, winner,
                                                                                    pa["mr"], 0, None, None, "demo", None))
        for g, (rid, w) in enumerate(zip(ids, wins), 1):
            con.execute("insert into games values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (rid, key, g, None, a, b, pa["char"], pb["char"], "Classic", "Modern",
                        pa["mr"], pb["mr"], w, "2-1" if w == a else "1-2", "P1, P2, P1" if w == a else "P2, P1, P2", None, None, None,
                        f"{pa['mr']} MR" if pa["mr"] else pa["league"], f"{pb['mr']} MR" if pb["mr"] else pb["league"]))
            for h in range(R.randint(10, 18)):
                att = R.choice([a, b]); vic = b if att == a else a
                con.execute("insert into hits (hit_id, set_key, replay_id, round, round_timer, attacker_id, victim_id, damage, starter, hits_in_combo, hit_kind, anti_air, situation, lens) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (f"{rid}-{h}", key, rid, R.randint(1, 3), R.randint(5, 99), att, vic, R.randint(300, 3500), R.choice(["2MK", "5HP", "Throw", "j.HK", "5MP"]),
                             R.randint(1, 6), R.choice(["clean hit", "counter hit", "punish counter", "throw"]), int(R.random() < 0.1),
                             R.choice(["neutral", "pressure", "oki", "punish"]), R.choice(LENSES)))
        doc_arch = []
        for pid, p, opp in ((a, pa, b), (b, pb, a)):
            games = len(wins)
            for m in METRICS:
                con.execute("insert into set_stats values (?,?,?,?)", (key, pid, m, R.randint(0, 6) * games if not m.endswith("_n") else 12 * games))
            con.execute("insert into set_stats values (?,?,?,?)", (key, pid, "games", games))
            for l in LENSES:
                con.execute("insert into set_stats values (?,?,?,?)", (key, pid, f"taken_share: {l}", round(R.random() / 3, 2)))
            arch = p["arch"] if R.random() < 0.75 else R.choice(ARCH)
            con.execute("insert into reads values (?,?,?,?,?,?,?,?,?,?,?)", (key, pid, p["char"], arch, "demo lean", R.choice(["Low", "Medium", "High"]),
                        "synthetic evidence", "How to beat this: block their early presses and frame-trap them; anti-air their jumps.", None, None, "demo"))
            sp = [dict(axis=ax, score=max(1, min(5, p["spec"][ax] + R.choice([-1, 0, 0, 1]))), evidence="synthetic") for ax in AXES]
            for x in sp: x["label"] = f"{LABEL[x['score']]} (demo)"
            if k == 0:   # like some real Full reviews: spectra only inside the review write-up, not in the spectra table
                doc_arch.append(dict(player=NAMES[pid - 1], spectra=sp))
            else:
                for x in sp:
                    con.execute("insert into spectra values (?,?,?,?,?,?)", (key, pid, x["axis"], x["score"], x["label"], x["evidence"]))
            for kind, area, habit in R.sample(HABITS, 3):
                hrow += 1
                con.execute("insert into habits values (?,?,?,?,?,?,?,?,?,?,?)", (hrow, key, pid, kind, area, habit, "G1 R1 @80", R.randint(1, 6), "demo fix", "Medium", "demo"))
        if doc_arch:
            con.execute("insert into review_docs values (?,?,?,?)", (key, "archetypes", json.dumps(doc_arch), date))
        if review == "Full":
            pred_w = a if R.random() < 0.6 else b
            verdict = "Right" if pred_w == winner else "Wrong"
            con.execute("insert into review_docs values (?,?,?,?)", (key, "prediction", json.dumps([{
                "written_at": f"{date}T10:00:00", "predicted": f"{NAMES[pred_w - 1]} wins 2-1 (Low confidence)",
                "actual": f"{NAMES[winner - 1]} wins {max(ga, gb)}-{min(ga, gb)}", "verdict": verdict,
                "what_happened": "Synthetic demo set.", "lessons": "Demo data."}]), date))
            con.execute("insert into review_docs values (?,?,?,?)", (key, "story_games", json.dumps([
                {"game_id": rid, "game_no": i + 1, "summary": "A synthetic game for the demo.", "turning_point": "Round 2 anti-air."} for i, rid in enumerate(ids)]), date))
    con.commit(); con.close()
    print("demo source written:", out)


if __name__ == "__main__":
    a = sys.argv
    main(a[1] if len(a) > 1 else "demo_source.db", int(a[a.index("--seed") + 1]) if "--seed" in a else 7)

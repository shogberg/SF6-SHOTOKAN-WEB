"""player_profile, player_archetype_summary, player_spectra_by_result, player_deviation.

Aggregates every set a player is in. Sentences are built from the numbers only (same approach as
the tools repo's profiles_from_db.py)."""
import collections, datetime, json, re, statistics
from common import AXES, ENDS, spectrum_label, confidence_for

RULES = {
    ("Temperament (defense)", 1): "they act on reversal timing after blocking and on wake-up: frame trap and meaty them, and block-then-punish their reversal",
    ("Temperament (defense)", 2): "their first action after blocking is often on reversal timing: short-gap frame traps catch it",
    ("Temperament (defense)", 4): "they wait and block: throw them, and take their Drive with plus strings",
    ("Temperament (defense)", 5): "they almost never press on defense: walk up and throw, and shimmy only after they tech",
    ("Temperament (offense)", 1): "they press again straight after a blocked attack: block, then hit the gap with your fastest button or perfect parry",
    ("Temperament (offense)", 5): "their offense waits after a blocked attack: take your turn back with a fast button or walk-up throw",
    ("Adaptability", 1): "they keep doing what you have already punished: punish it the same way again",
    ("Adaptability", 2): "they are slow to drop what gets punished: repeat what worked until they change",
    ("Adaptability", 5): "they adjust between games: show a new option each game rather than repeating the one that worked",
    ("Risk tolerance", 4): "they take more risks than most: block first and punish the reversal, Drive Impact or jump",
    ("Risk tolerance", 5): "they gamble (reversals, Drive Impact, raw Drive Rush, jumps): block, bait and punish the gambles",
    ("Risk tolerance", 1): "they take few risks: open them up with throws and Drive pressure, not big reads",
    ("Initiative", 1): "they wait for you: walk them to the corner in small steps instead of pressing into their pokes",
    ("Initiative", 4): "they walk forward a lot: stand at your poke range and whiff-punish or counter-poke the walk-in",
    ("Initiative", 5): "they come forward: hold your space with pokes and anti-airs and whiff-punish their approach",
    ("Composure", 4): "they get busier after taking damage: block first after you land a big combo",
    ("Composure", 5): "they press more after a big hit or a lost round: stay patient and block right after you land damage",
    ("Variety", 1): "their after-block and wake-up choices are scripted: read the default and hard-punish it",
    ("Variety", 2): "they lean on one or two defensive defaults: find them early and call them out",
    ("Resource use", 1): "they sit on Drive and super: respect their reversal and parry, and don't gamble into full meter",
    ("Resource use", 5): "they spend Drive freely: block their pressure, make them spend, and corner them when they burn out",
    ("Space", 1): "they give ground and spend rounds cornered: keep them there with plus strings and throws, and cover the jump out",
    ("Space", 5): "they take ground and keep you cornered: don't walk back into the wall, and spend Drive or a reversal to get out",
}
LENS_SHORT = {"Pressed in their pressure / on wake-up": "pressing in pressure or on wake-up", "Pressed at mid range": "pressing at mid range",
              "Walked in": "walking in", "Teched a throw": "teching throws", "Blocking, opened up": "getting opened up while blocking",
              "Jumped": "jumping", "Jumped in on (no anti-air)": "being jumped in on", "Own offense beaten by a reversal": "their offense beaten by a reversal",
              "Drive Rush / Impact checked": "Drive Rush / Impact getting checked", "Unsafe move punished": "unsafe moves punished"}
SKIP_PATTERNS = ("first action after blocking",)


def build(con, cfg):
    me = (con.execute("select value from settings where key='me'").fetchone() or [None])[0]
    players = {r["player_id"]: r for r in con.execute("select * from players")}
    ps_all = collections.defaultdict(list)
    # played order: date, then the set's first game time (set keys are replay IDs, so they don't sort by time)
    for r in con.execute("""select ps.* from player_set ps
                            order by ps.played_date, (select min(g.played_time) from games g where g.set_key = ps.set_key), ps.set_key"""):
        ps_all[r["player_id"]].append(r)
    n = 0
    for pid, sets in ps_all.items():
        p = players.get(pid)
        if not p:
            continue
        keys = [s["set_key"] for s in sets]
        ph = ",".join("?" * len(keys))
        won = sum(s["won"] or 0 for s in sets); gw = sum(s["games_won"] or 0 for s in sets); gl = sum(s["games_lost"] or 0 for s in sets)
        chars = collections.Counter(s["character"] for s in sets)
        # rank shown for the player: each character's most recent rated set, then the highest MR among them (a player
        # trying a new character keeps their main's rank); with no MR on any character, the most recent rated set
        by_char = {}
        for s in sets:
            if s["mr"] or s["league"]:
                by_char[s["character"]] = s
        rated = [s for s in by_char.values() if s["mr"]]
        latest = max(rated, key=lambda s: s["mr"]) if rated else next((s for s in reversed(sets) if s["mr"] or s["league"]), sets[-1])
        reviews = collections.Counter(s["review"] for s in sets)

        st = collections.defaultdict(float); games = 0
        for r in con.execute(f"select metric, value from set_stats where player_id=? and set_key in ({ph})", [pid, *keys]):
            if r["metric"] == "games": games += r["value"]
            elif not r["metric"].startswith("taken_"): st[r["metric"]] += r["value"]
        games = games or (gw + gl) or 1
        pg = lambda m: round(st.get(m, 0) / games, 1)
        pct = lambda a, b: round(100 * st.get(a, 0) / st[b]) if st.get(b) else None
        ab, wu = pct("after_block_attack", "after_block_n"), pct("wake_up_attack", "wake_up_n")
        per_game = dict(throws=pg("throws"), throw_techs=pg("throw_techs"), anti_airs=pg("anti_airs"), counter_hits=pg("counter_hits"),
                        punish_counters=pg("punish_counters"), raw_drive_rush=pg("raw_drive_rush"), burnouts=pg("burnouts"),
                        perfect_parries=pg("perfect_parries"), after_block_attack_pct=ab, wake_up_attack_pct=wu, games=int(games))

        # what opponents did to them
        os_ = collections.defaultdict(float)
        for s in sets:
            for r in con.execute("select metric, value from set_stats where player_id=? and set_key=?", (s["opp_id"], s["set_key"])):
                if r["metric"] != "games": os_[r["metric"]] += r["value"]
        opg = lambda m: round(os_.get(m, 0) / games, 1)
        opp_did = dict(counter_hits_taken=round(opg("counter_hits") + opg("punish_counters"), 1), anti_aired=opg("anti_airs"), thrown=opg("throws"))

        # spectra: overall and by result
        won_by_set = {s["set_key"]: s["won"] for s in sets}
        sp = collections.defaultdict(list); spw = collections.defaultdict(list); spl = collections.defaultdict(list); ev = collections.defaultdict(list)
        for r in con.execute(f"select set_key, axis, score, evidence from spectra where player_id=? and set_key in ({ph})", [pid, *keys]):
            if not r["score"]: continue
            sp[r["axis"]].append(r["score"]); ev[r["axis"]].append(r["evidence"])
            if won_by_set.get(r["set_key"]) is not None:   # unfinished sets count in the overall spectra only
                (spw if won_by_set[r["set_key"]] else spl)[r["axis"]].append(r["score"])
        spectra = []
        for a in AXES:
            v = sp[a]
            if not v:
                spectra.append(dict(axis=a, left=ENDS[a][0], right=ENDS[a][1], score=None, label=None, n=0, evidence="not enough data", per_set=[])); continue
            m = statistics.mean(v); s_ = int(round(m))
            spectra.append(dict(axis=a, left=ENDS[a][0], right=ENDS[a][1], score=s_, label=spectrum_label(a, s_), mean=round(m, 2),
                                lo=min(v), hi=max(v), n=len(v), evidence=ev[a][-1], per_set=v))
            mw = statistics.mean(spw[a]) if spw[a] else None; ml = statistics.mean(spl[a]) if spl[a] else None
            con.execute("insert into player_spectra_by_result values (?,?,?,?,?,?,?,?)",
                        (pid, a, mw and round(mw, 2), len(spw[a]), ml and round(ml, 2), len(spl[a]), round(m, 2), round(statistics.pstdev(v), 2)))

        # archetype
        arch_sets = [s for s in sets if s["archetype"]]
        cnt = collections.Counter(s["archetype"] for s in arch_sets)
        top, top_n = (None, 0)
        if cnt:
            mx = max(cnt.values()); top = next(s["archetype"] for s in reversed(arch_sets) if cnt[s["archetype"]] == mx); top_n = cnt[top]
        lean = next((s["lean"] for s in reversed(arch_sets) if s["archetype"] == top and s["lean"]), None)
        if lean and any(ch.isdigit() for ch in lean): lean = None
        conf = "Low" if len(arch_sets) < 2 else "High" if len(arch_sets) >= 4 and top_n / len(arch_sets) >= 0.75 else "Medium"
        devs = [s for s in arch_sets if s["is_deviation"]]
        for a, k in cnt.items():
            w = sum(1 for s in arch_sets if s["archetype"] == a and s["won"] == 1)
            l_ = sum(1 for s in arch_sets if s["archetype"] == a and s["won"] == 0)
            con.execute("insert into player_archetype_summary values (?,?,?,?,?)", (pid, a, k, w, l_))
        dev_ctx = collections.Counter()
        for s in devs:
            if s["won"] is not None: dev_ctx[(top, s["archetype"], "won" if s["won"] else "lost")] += 1
            if s["lost_game1"]: dev_ctx[(top, s["archetype"], "after losing game 1")] += 1
            if s["opp_archetype"]: dev_ctx[(top, s["archetype"], f"vs {s['opp_archetype']}")] += 1
            if len(chars) > 1: dev_ctx[(top, s["archetype"], f"on {s['character']}")] += 1
        con.executemany("insert into player_deviation values (?,?,?,?,?)", [(pid, f, t, c, k) for (f, t, c), k in dev_ctx.items()])

        # habits
        hab = collections.defaultdict(lambda: [0, 0])
        for r in con.execute(f"select kind, habit, times from habits where player_id=? and set_key in ({ph})", [pid, *keys]):
            if any(x in r["habit"] for x in SKIP_PATTERNS): continue
            k = (r["kind"], r["habit"]); hab[k][0] += 1; hab[k][1] += r["times"] or 0
        def top_h(kind, n=4):
            xs = sorted(((v[0], v[1], h) for (k, h), v in hab.items() if k == kind), reverse=True)[:n]
            return "; ".join(h + ((f" ({t}×" + (f" in {s} sets" if s > 1 else "") + ")") if t and "×" not in h else (f" (in {s} sets)" if s > 1 else "")) for s, t, h in xs)
        derived = []
        if opp_did["counter_hits_taken"] >= 5: derived.append(f"got counter-hit {opp_did['counter_hits_taken']}× a game")
        if opp_did["anti_aired"] >= 1.5: derived.append(f"anti-aired {opp_did['anti_aired']}× a game")
        if opp_did["thrown"] >= 1.5 and per_game["throw_techs"] < opp_did["thrown"] / 2: derived.append(f"thrown {opp_did['thrown']}× a game, teching {per_game['throw_techs']}")
        if per_game["burnouts"] >= 0.5 and not any(h.startswith("Burn") for (k, h) in hab if k == "Leak"): derived.append(f"burned out {per_game['burnouts']}× a game")
        if (ab or 0) >= 40: derived.append(f"attacks first after blocking {ab}% of the time")
        leaks = "; ".join(x for x in [top_h("Leak"), "; ".join(derived)] if x)

        # the same strengths / leaks over recent windows (all time is the columns above)
        def window(sub):
            if not sub: return None
            ks = [s["set_key"] for s in sub]; q = ",".join("?" * len(ks))
            h = collections.defaultdict(lambda: [0, 0])
            for r in con.execute(f"select kind, habit, times from habits where player_id=? and set_key in ({q})", [pid, *ks]):
                if any(x in r["habit"] for x in SKIP_PATTERNS): continue
                h[(r["kind"], r["habit"])][0] += 1; h[(r["kind"], r["habit"])][1] += r["times"] or 0
            def top(kind, n=4):
                xs = sorted(((v[0], v[1], hb) for (k, hb), v in h.items() if k == kind), reverse=True)[:n]
                return "; ".join(hb + ((f" ({t}×" + (f" in {c} sets" if c > 1 else "") + ")") if t and "×" not in hb else (f" (in {c} sets)" if c > 1 else "")) for c, t, hb in xs)
            m = collections.defaultdict(float); o = collections.defaultdict(float); g = 0
            for s in sub:
                for r in con.execute("select metric, value from set_stats where player_id=? and set_key=?", (pid, s["set_key"])):
                    if r["metric"] == "games": g += r["value"]
                    elif not r["metric"].startswith("taken_"): m[r["metric"]] += r["value"]
                for r in con.execute("select metric, value from set_stats where player_id=? and set_key=?", (s["opp_id"], s["set_key"])):
                    if r["metric"] != "games": o[r["metric"]] += r["value"]
            g = g or sum((s["games_won"] or 0) + (s["games_lost"] or 0) for s in sub) or 1
            ch = round((o["counter_hits"] + o["punish_counters"]) / g, 1); aa = round(o["anti_airs"] / g, 1); th = round(o["throws"] / g, 1)
            tt = round(m["throw_techs"] / g, 1); bo = round(m["burnouts"] / g, 1)
            abw = round(100 * m["after_block_attack"] / m["after_block_n"]) if m["after_block_n"] else None
            d = []
            if ch >= 5: d.append(f"got counter-hit {ch}× a game")
            if aa >= 1.5: d.append(f"anti-aired {aa}× a game")
            if th >= 1.5 and tt < th / 2: d.append(f"thrown {th}× a game, teching {tt}")
            if bo >= 0.5 and not any(hb.startswith("Burn") for (k, hb) in h if k == "Leak"): d.append(f"burned out {bo}× a game")
            if (abw or 0) >= 40: d.append(f"attacks first after blocking {abw}% of the time")
            won_ = sum(s["won"] or 0 for s in sub)
            return dict(sets=len(sub), won=won_, lost=sum(1 for s in sub if s["won"] == 0), first=sub[0]["played_date"], last=sub[-1]["played_date"],
                        games=int(g), strengths=top("Strength"), leaks="; ".join(x for x in [top("Leak"), "; ".join(d)] if x))
        today = datetime.date.today()
        week = [s for s in sets if s["played_date"] and (today - datetime.date.fromisoformat(s["played_date"][:10])).days < 7]
        windows = dict(recent10=window(sets[-10:]), last7=window(week), all=dict(sets=len(sets), won=won, lost=sum(1 for s in sets if s["won"] == 0),
                       first=sets[0]["played_date"], last=sets[-1]["played_date"], games=int(games), strengths=top_h("Strength"), leaks=leaks))

        # damage taken
        share = collections.defaultdict(list)
        for r in con.execute(f"select metric, value from set_stats where player_id=? and set_key in ({ph}) and metric like 'taken_share:%'", [pid, *keys]):
            k = r["metric"].split(": ", 1)[1]
            if k != "Unclear / super": share[k].append(r["value"])
        sh = sorted(((statistics.mean(v), k) for k, v in share.items()), reverse=True)
        taken = ", ".join(f"{LENS_SHORT.get(k, k)} {round(100 * v)}%" for v, k in sh[:3])

        # summary + how to beat
        opps = sorted({s["opp_id"] for s in sets})
        names = [players[o]["name"] for o in opps if o in players]
        vs = ", ".join(names) if len(names) <= 3 else f"{len(names)} opponents"
        summ = (f"{top or 'Unread'} {chars.most_common(1)[0][0]} player{' (' + lean + ')' if lean else ''}. Played {vs}. "
                f"Per game: {per_game['throws']} throws, {per_game['throw_techs']} throw techs, {per_game['anti_airs']} anti-airs, "
                f"{per_game['counter_hits']} counter hits, {per_game['raw_drive_rush']} raw Drive Rushes, {per_game['burnouts']} burnouts.")
        if ab is not None: summ += f" Attacks first after blocking {ab}% of the time" + (f" and on wake-up {wu}%" if wu is not None else "") + "."
        if taken: summ += f" Most damage taken came from {taken}."
        ext = [x for x in spectra if x["score"] in (1, 5)]
        if ext: summ += " Stands out on: " + ", ".join(f"{x['axis']} ({x['label'].lower()})" for x in ext) + "."
        tips = [RULES[(x["axis"], x["score"])] for x in spectra if (x["axis"], x["score"]) in RULES]
        notes = []
        reads = con.execute(f"select counter_note from reads where player_id=? and set_key in ({ph})", [pid, *keys]).fetchall()
        for (cn,) in reads:
            cn = (cn or "").strip()
            cn = re.sub(r"^(How to beat (this|them|him|her): |What costs (you|him|her|them)( in this set)?: )", "", cn)
            for frag in [f.strip().rstrip(".") for f in re.split(r"[;,]\s(?![^()]*\))", cn)]:
                frag = re.sub(r"^(What costs (you|him|her|them)( in this set)?|How to beat (this|them|him|her)): ", "", frag)
                if frag and frag not in notes: notes.append(frag)
        beat = " ".join(t[0].upper() + t[1:] + "." for t in tips[:4])
        if notes: beat += (" " if beat else "") + ("What cost them" if p["name"] == me else "From the reviews") + ": " + "; ".join(notes[:5]) + "."

        con.execute("insert into player_profile values (?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?, ?, ?,?,?,?,?,?, ?,?,?,?,?, ?,?,?,?)", (
            pid, p["name"], p["cfn_id"], p["region"], json.dumps(chars.most_common()),
            len(sets), won, gw, gl, sets[0]["played_date"], sets[-1]["played_date"],
            latest["mr"], latest["league"], latest["band"], latest["band_label"], json.dumps(dict(reviews)),
            top, top_n, lean, conf, round(len(devs) / len(arch_sets), 2) if arch_sets else None, len(devs),
            summ, top_h("Strength"), leaks, top_h("Pattern", 3), beat,
            json.dumps(spectra), json.dumps(per_game), json.dumps(opp_did), json.dumps(windows)))
        n += 1
    return n

"""Build a SHOTOKAN Web snapshot from a local sf6.db, validate it, and install or upload it.

  python publish.py --source sf6.db --out ./data            build + validate + swap into ./data/current.db
  python publish.py --source sf6.db --target user@host:/srv/shotokan/data   ... + upload over SSH and swap remotely
  python publish.py --source sf6.db --dry-run               build + validate only
  options: --config publish.json  (merge local names into CFN players, observations dir, anonymize)

Nothing here holds credentials: uploads use your SSH key/agent.
"""
import argparse, datetime, json, os, shutil, sqlite3, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import SCHEMA_VERSION, BANDS, NON_MASTER, UNKNOWN, WEIGHTS, JP_OFFSET  # noqa: E402
import derive  # noqa: E402

# source tables copied as-is, minus private columns
SOURCE = {
    "players": None, "player_names": None, "sets": ["dashboard", "ingested_at"], "games": ["capture_file"],
    "hits": None, "events": None, "resources": None, "parries": None, "timings": None, "set_stats": None, "game_stats": None,
    "reads": None, "spectra": None, "habits": None, "usage": None, "review_docs": None, "settings": None,
}
KEEP_SETTINGS = ("me",)


def copy_source(src, dst, cfg):
    s = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
    for t, drop in SOURCE.items():
        cols = [r[1] for r in s.execute(f"pragma table_info({t})")]
        if not cols:
            continue
        keep = [c for c in cols if c not in (drop or [])]
        if t == "players" and "region" not in keep:
            keep_sql = ", ".join(keep) + ", NULL AS region"; cols_out = keep + ["region"]
        else:
            keep_sql = ", ".join(keep); cols_out = keep
        dst.execute(f"create table {t} ({', '.join(cols_out)})")
        rows = s.execute(f"select {keep_sql} from {t}").fetchall()
        if t == "settings":
            rows = [r for r in rows if r[0] in KEEP_SETTINGS]
        dst.executemany(f"insert into {t} values ({','.join('?' * len(cols_out))})", rows)
    s.close()
    backfill_spectra(dst)
    merge_players(dst, cfg.get("merge") or {})
    if cfg.get("anonymize"):
        anonymize(dst)


def backfill_spectra(con):
    """Some reviews (Full / Tournament dashboards) keep a player's spectra only inside review_docs 'archetypes'.
    Add them to the spectra table where it has nothing for that set and player. Runs before merge_players,
    so names match the players as they were named in that review."""
    import json as _json
    ids = {r[1]: r[0] for r in con.execute("select player_id, name from players")}
    ids.update({r[1]: r[0] for r in con.execute("select player_id, name from player_names") if r[1] not in ids})
    have = {(r[0], r[1]) for r in con.execute("select distinct set_key, player_id from spectra")}
    added = 0
    for key, rows in con.execute("select set_key, rows from review_docs where dataset='archetypes'").fetchall():
        try:
            items = _json.loads(rows) or []
        except ValueError:
            continue
        for it in items:
            pid = ids.get(it.get("player"))
            sp = it.get("spectra")
            if isinstance(sp, str):
                try: sp = _json.loads(sp)
                except ValueError: sp = None
            if pid is None or not sp or (key, pid) in have:
                continue
            for x in sp:
                if x.get("axis"):
                    con.execute("insert into spectra (set_key, player_id, axis, score, label, evidence) values (?,?,?,?,?,?)",
                                (key, pid, x["axis"], x.get("score"), x.get("label"), x.get("evidence")))
            have.add((key, pid)); added += 1
    if added:
        print(f"  spectra filled from review write-ups for {added} player-sets")


def merge_players(con, merge):
    """merge {"local name": "canonical name"}: repoint every reference from the local player to the canonical one."""
    ids = {r[1]: r[0] for r in con.execute("select player_id, name from players")}
    refs = [("sets", "focus_player_id"), ("sets", "opp_player_id"), ("sets", "winner_player_id"), ("games", "p1_player_id"),
            ("games", "p2_player_id"), ("games", "winner_player_id"), ("hits", "attacker_id"), ("hits", "victim_id")]
    refs += [(t, "player_id") for t in ("events", "resources", "parries", "timings", "set_stats", "game_stats", "reads", "spectra", "habits", "usage", "player_names")]
    have = {r[0] for r in con.execute("select name from sqlite_master where type='table'")}
    refs = [(t, c) for t, c in refs if t in have]   # game_stats only exists in newer source databases
    for local, canon in merge.items():
        a, b = ids.get(local), ids.get(canon)
        if a is None or b is None or a == b:
            print(f"  merge skipped: {local} -> {canon}"); continue
        for t, c in refs:
            con.execute(f"update {t} set {c}=? where {c}=?", (b, a))
        con.execute("delete from player_names where player_id=? and name=?", (b, local))
        con.execute("insert into player_names (player_id, name) values (?, ?)", (b, local))
        con.execute("delete from players where player_id=?", (a,))
        print(f"  merged {local} into {canon}")


def anonymize(con):
    me = (con.execute("select value from settings where key='me'").fetchone() or [None])[0]
    for i, (pid, name) in enumerate(con.execute("select player_id, name from players order by player_id").fetchall(), 1):
        if name != me:
            con.execute("update players set name=?, cfn_id=NULL where player_id=?", (f"Player {i:03d}", pid))
    con.execute("delete from player_names")
    con.execute("update review_docs set rows='[]'")   # written reviews name players in free text


def build(source, out_file, cfg):
    if os.path.exists(out_file):
        os.remove(out_file)
    con = sqlite3.connect(out_file); con.row_factory = sqlite3.Row
    copy_source(source, con, cfg)
    con.executescript(open(os.path.join(HERE, "schema.sql")).read())
    counts = {}
    for mod in derive.ORDER:
        counts[mod.__name__.split(".")[-1]] = mod.build(con, cfg)
    meta = dict(schema_version=SCHEMA_VERSION, built_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                snapshot_id=os.path.splitext(os.path.basename(out_file))[0], source_name=os.path.basename(source),
                bands=json.dumps([dict(id=b[0], label=b[1], lo=b[2], hi=b[3]) for b in BANDS] + [dict(id=NON_MASTER[0], label=NON_MASTER[1]), dict(id=UNKNOWN[0], label=UNKNOWN[1])]),
                weights=json.dumps(WEIGHTS), jp_offset=str(JP_OFFSET), jp_adjustment="deferred", anonymized=str(bool(cfg.get("anonymize"))),
                counts=json.dumps(counts))
    con.executemany("insert into snapshot_meta values (?,?)", meta.items())
    con.commit(); con.execute("vacuum"); con.close()
    return counts


def validate(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    errs = []
    if con.execute("pragma integrity_check").fetchone()[0] != "ok":
        errs.append("integrity_check failed")
    v = dict(con.execute("select key, value from snapshot_meta")).get("schema_version")
    if v != SCHEMA_VERSION:
        errs.append(f"schema_version {v} != {SCHEMA_VERSION}")
    for t in ("players", "sets", "player_set", "set_summary", "player_profile"):
        if not con.execute(f"select count(*) from {t}").fetchone()[0]:
            errs.append(f"{t} is empty")
    orphans = con.execute("select count(*) from player_set where player_id not in (select player_id from players)").fetchone()[0]
    if orphans:
        errs.append(f"{orphans} player_set rows point to missing players")
    cols = [r[1] for r in con.execute("pragma table_info(games)")]
    if "capture_file" in cols:
        errs.append("private column games.capture_file present")
    # recompute one profile number directly
    r = con.execute("select player_id, sets, sets_won from player_profile order by sets desc limit 1").fetchone()
    if r:
        n, w = con.execute("select count(*), sum(winner_player_id=?) from sets where focus_player_id=? or opp_player_id=?", (r[0], r[0], r[0])).fetchone()
        if (n, w) != (r[1], r[2]):
            errs.append(f"profile check failed for player {r[0]}: {(r[1], r[2])} vs {(n, w)}")
    con.close()
    return errs


def install_local(snap, data_dir, keep=5):
    """Same steps as deploy/swap_snapshot.sh: move into snapshots/, repoint current.db, keep the last N."""
    sd = os.path.join(data_dir, "snapshots"); os.makedirs(sd, exist_ok=True)
    dst = os.path.join(sd, os.path.basename(snap)); shutil.move(snap, dst)
    cur = os.path.join(data_dir, "current.db"); tmp = cur + ".new"
    try:
        if os.path.lexists(tmp): os.remove(tmp)
        os.symlink(os.path.relpath(dst, data_dir), tmp); os.replace(tmp, cur)
    except (OSError, NotImplementedError):          # Windows without symlink rights: copy instead
        shutil.copyfile(dst, tmp); os.replace(tmp, cur)
    olds = sorted(f for f in os.listdir(sd) if f.endswith(".db"))
    for f in olds[:-keep]:
        os.remove(os.path.join(sd, f))
    return cur


def upload(snap, target):
    host, path = target.split(":", 1)
    subprocess.run(["scp", snap, f"{host}:{path.rstrip('/')}/incoming/"], check=True)
    subprocess.run(["ssh", host, f"sudo -u shotokan /srv/shotokan/deploy/swap_snapshot.sh {path.rstrip('/')}/incoming/{os.path.basename(snap)}"], check=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", help="data folder to install into (creates snapshots/ and current.db)")
    ap.add_argument("--target", help="user@host:/srv/shotokan/data to upload to")
    ap.add_argument("--config", help="JSON: {merge: {local: canonical}, observations_dir, anonymize}")
    ap.add_argument("--anonymize", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    cfg = json.load(open(a.config)) if a.config else {}
    if a.anonymize: cfg["anonymize"] = True
    if cfg.get("observations_dir") and a.config:
        cfg["observations_dir"] = os.path.join(os.path.dirname(os.path.abspath(a.config)), cfg["observations_dir"])
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    work = os.path.join(HERE, "out"); os.makedirs(work, exist_ok=True)
    snap = os.path.join(work, f"shotokan_web-{stamp}.db")
    counts = build(a.source, snap, cfg)
    print("built", snap, counts)
    errs = validate(snap)
    if errs:
        print("VALIDATION FAILED:\n  " + "\n  ".join(errs)); return 1
    print("validated")
    if a.dry_run:
        return 0
    if a.target:
        upload(snap, a.target); print("uploaded and swapped on", a.target)
    if a.out:
        print("installed", install_local(snap, a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())

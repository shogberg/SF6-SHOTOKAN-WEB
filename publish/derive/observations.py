"""observations: dated notes from markdown files with front matter (cfg['observations_dir'])."""
import json, os, glob, re


def parse(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
            meta[k.strip()] = v
    return meta, m.group(2).strip()


def build(con, cfg):
    d = cfg.get("observations_dir")
    if not d or not os.path.isdir(d):
        return 0
    n = 0
    for p in sorted(glob.glob(os.path.join(d, "*.md"))):
        r = parse(p)
        if not r:
            continue
        meta, body = r
        oid = meta.get("id") or os.path.splitext(os.path.basename(p))[0]
        con.execute("insert or replace into observations values (?,?,?,?,?,?,?)", (
            oid, meta.get("date"), meta.get("topic", "Other"), meta.get("title", oid), body,
            json.dumps(meta.get("evidence") or []), meta.get("supersedes")))
        n += 1
    return n

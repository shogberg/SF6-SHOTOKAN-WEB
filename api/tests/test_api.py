def test_health(client):
    r = client.get("/healthz"); assert r.status_code == 200 and r.json()["ok"]


def test_search_and_profile(client):
    r = client.get("/api/v1/search", params={"q": "ryu"}).json()
    assert r["snapshot"]["schema_version"].startswith("1.")
    pid = r["data"][0]["player_id"]
    p = client.get(f"/api/v1/players/{pid}").json()["data"]
    assert p["name"] == "Ryuko" and p["sets"] > 0 and len(p["spectra"]) == 8
    a = client.get(f"/api/v1/players/{pid}/archetypes").json()["data"]
    assert a["summary"] and a["timeline"]


def test_sets_and_detail(client):
    s = client.get("/api/v1/players/1/sets").json()
    assert s["totals"]["sets"] == len(s["data"]) > 0
    won = client.get("/api/v1/players/1/sets", params={"result": "won"}).json()
    assert all(x["won"] == 1 for x in won["data"])
    d = client.get(f"/api/v1/sets/{s['data'][0]['set_key']}").json()["data"]
    assert d["summary"] and d["games"] and len(d["players"]) == 2


def test_prediction_present(client):
    sets = client.get("/api/v1/players/1/sets").json()["data"]
    withp = [x for x in sets if x["has_prediction"]]
    assert withp
    d = client.get(f"/api/v1/sets/{withp[0]['set_key']}").json()["data"]
    assert d["predictions"][0]["verdict"] in ("Right", "Wrong")


def test_h2h(client):
    opp = client.get("/api/v1/players/1").json()["data"]["top_opponents"][0]["player_id"]
    h = client.get(f"/api/v1/h2h/1/{opp}").json()["data"]
    assert h["record"]["sets"] == len(h["sets"]) > 0


def test_placeholders_and_404(client):
    assert client.get("/api/v1/matchups").status_code == 200
    assert client.get("/api/v1/matchups/Ryu/Ken").status_code == 501
    assert client.get("/api/v1/analysis/mr-bands").status_code == 200
    assert client.get("/api/v1/analysis/observations").status_code == 200
    assert client.get("/api/v1/players/99999").status_code == 404


def test_spectra_from_review_writeups(client):
    # demo set 0 keeps its spectra only in review_docs 'archetypes'; publish must fill them in
    sets = client.get("/api/v1/players/1/sets").json()["data"]
    first = [x for x in sets if x["set_key"].startswith("D000")][0]
    d = client.get(f"/api/v1/sets/{first['set_key']}").json()["data"]
    assert all(len(p["spectra"]) == 8 for p in d["players"])
    prof = client.get("/api/v1/players/1").json()["data"]
    assert all(s["score"] for s in prof["spectra"])


def test_sets_search_paginated(client):
    r = client.get("/api/v1/sets", params={"q": "Ryuko"}).json()
    assert r["player"]["name"] == "Ryuko" and r["page"]["per_page"] == 25
    assert len(r["data"]) == min(25, r["page"]["total"]) and r["page"]["total"] == r["totals"]["sets"]
    if r["page"]["pages"] > 1:
        p2 = client.get("/api/v1/sets", params={"player": r["player"]["player_id"], "page": 2}).json()
        assert p2["page"]["page"] == 2 and {x["set_key"] for x in p2["data"]}.isdisjoint({x["set_key"] for x in r["data"]})
    # a partial name that matches several players returns candidates to pick from
    many = client.get("/api/v1/sets", params={"q": "o"}).json()
    assert many["player"] is None and len(many["candidates"]) > 1 and many["data"] == []
    # no query: every set, paged
    allr = client.get("/api/v1/sets", params={"per_page": 10}).json()
    assert len(allr["data"]) == 10 and allr["page"]["total"] == 40
    # player sets endpoint is paged too
    ps = client.get("/api/v1/players/1/sets", params={"per_page": 5}).json()
    assert len(ps["data"]) == 5 and ps["totals"]["sets"] == ps["page"]["total"]


def test_players_list(client):
    r = client.get("/api/v1/players").json()["data"]
    assert r and {"player_id", "name", "sets", "sets_won", "characters"} <= set(r[0])
    assert r == sorted(r, key=lambda p: p["name"].lower())


def test_traits(client):
    d = client.get("/api/v1/analysis/traits").json()["data"]
    assert d["pairs"] > 0 and d["rows"]
    groups = {r["group"] for r in d["rows"]}
    assert {"Offense", "Defense", "Drive"} <= groups
    for r in d["rows"]:
        assert r["n"] > 0 and (r["winner_higher"] is None or 0 <= r["winner_higher"] <= 1)


def test_profile_by_character(client):
    pid = client.get("/api/v1/players").json()["data"][0]["player_id"]
    p = client.get(f"/api/v1/players/{pid}").json()["data"]
    assert p["by_character"], "every player with a set has at least one character row"
    c = p["by_character"][0]
    assert c["games"] >= 1 and "throws" in c["per_game"] and len(c["spectra"]) == 8
    assert sum(x["sets"] for x in p["by_character"]) == p["sets"]


def test_traits_views(client):
    all_ = client.get("/api/v1/analysis/traits").json()["data"]
    oth = client.get("/api/v1/analysis/traits?view=others").json()["data"]
    me = client.get("/api/v1/analysis/traits?view=me").json()["data"]
    assert all_["view"] == "all" and oth["view"] == "others" and me["view"] == "me"
    assert me["me"] is not None, "the demo snapshot has a configured player (settings 'me')"
    assert oth["pairs"] <= all_["pairs"]
    assert me["won"] + me["lost"] == me["pairs"]
    for r in me["rows"]:
        assert r["winner_higher"] is None and r["n_won"] + r["n_lost"] == r["n"]


def test_set_baseline_field(client):
    k = client.get("/api/v1/sets").json()["data"][0]["set_key"]
    d = client.get(f"/api/v1/sets/{k}").json()["data"]
    assert all(isinstance(p["baseline"], list) for p in d["players"])


def test_player_mr_history(client):
    pid = client.get("/api/v1/players").json()["data"][0]["player_id"]
    r = client.get(f"/api/v1/players/{pid}/mr").json()
    assert "characters" in r and "phases" in r and isinstance(r["data"], list)
    for p in r["data"]:
        assert p["mr_after"] == p["mr"] + p["change"] and p["character"] in r["characters"]
    assert [p["at"] for p in r["data"]] == sorted(p["at"] for p in r["data"])
    if r["data"]:
        d = r["data"][-1]["at"][:10]
        later = client.get(f"/api/v1/players/{pid}/mr", params={"date_from": d}).json()["data"]
        assert later and all(p["at"][:10] >= d for p in later)
    assert client.get("/api/v1/players/999999/mr").status_code == 404


def test_winrates(client):
    w = client.get("/api/v1/players/1/winrates").json()["data"]
    assert w and all(c["games"] == c["won"] + c["lost"] for c in w)
    for c in w:
        assert sum(o["games"] for o in c["by_opponent_character"]) == c["games"]
        assert sum(b["games"] for b in c["by_mr"]) == c["mr_games"] <= c["games"]
        assert all(b["band"] == f"{b['mr_from']}-{b['mr_from'] + 99}" and b["mr_from"] % 100 == 0 for b in c["by_mr"])
    r = client.get("/api/v1/players/1/winrates", params={"context": "ranked"}).json()["data"]
    assert sum(c["games"] for c in r) <= sum(c["games"] for c in w)
    assert client.get("/api/v1/players/999999/winrates").status_code == 404


def test_stats_pages(client):
    m = client.get("/api/v1/analysis/mr-bands").json()["data"]
    assert m["bands"] and m["metrics"] and all(set(r["bands"]) == {b["id"] for b in m["bands"]} for r in m["metrics"])
    c = client.get("/api/v1/matchups").json()
    assert c["bands"][0]["id"] == "all" and c["data"]
    for ch in c["data"]:
        assert sum(v["games"] for v in ch["vs"]) == ch["games"]
        assert ch["games_non_mirror"] == ch["won"] + ch["lost"]
    b = c["bands"][1]["id"]
    cb = client.get("/api/v1/matchups", params={"band": b}).json()["data"]
    assert sum(x["games"] for x in cb) <= sum(x["games"] for x in c["data"])
    a = client.get("/api/v1/analysis/archetypes").json()["data"]
    assert [s["archetype"] for s in a["summary"]] == ["Aggressive", "Balanced", "Defensive", "Fundamentalist"]
    assert sum(s["player_sets"] for s in a["summary"]) == a["player_sets"]


def test_context_filter(client):
    for path in ("/api/v1/analysis/mr-bands", "/api/v1/matchups"):
        n = {}
        for ctx in ("all", "ranked", "other"):
            r = client.get(path, params={"context": ctx})
            assert r.status_code == 200
            d = r.json()["data"]
            n[ctx] = sum(b["player_sets"] for b in d["bands"]) if "bands" in d else sum(c["games"] for c in d)
        assert n["ranked"] + n["other"] == n["all"]


def test_player_flags(client):
    p = client.get("/api/v1/players/1").json()["data"]
    assert p["flags"] and p["flags"][0]["flag"] == "notable" and p["flags"][0]["label"] == "Notable player"
    lst = client.get("/api/v1/players").json()["data"]
    assert any(x["flags"] for x in lst if x["player_id"] == 1)
    assert all("flags" in x for x in lst)

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
    assert client.get("/api/v1/matchups").status_code == 501
    assert client.get("/api/v1/analysis/mr-bands").status_code == 501
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

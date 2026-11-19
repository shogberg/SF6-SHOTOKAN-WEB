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

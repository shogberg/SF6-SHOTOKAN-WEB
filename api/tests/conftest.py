import os, subprocess, sys, pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    d = tmp_path_factory.mktemp("snap")
    src = d / "demo_source.db"
    subprocess.run([sys.executable, os.path.join(ROOT, "publish", "demo", "make_demo.py"), str(src)], check=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "publish", "publish.py"), "--source", str(src), "--out", str(d / "data")], check=True)
    os.environ["SHOTOKAN_DB"] = str(d / "data" / "current.db")
    sys.path.insert(0, os.path.join(ROOT, "api"))
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)

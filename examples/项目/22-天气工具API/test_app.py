from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_weather() -> None:
    r = client.get("/weather/上海")
    assert r.status_code == 200
    assert r.json()["summary"].startswith("晴")

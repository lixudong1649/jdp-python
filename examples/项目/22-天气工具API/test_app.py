from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_weather_known_city() -> None:
    r = client.get("/weather/上海")
    assert r.status_code == 200
    assert r.json()["summary"].startswith("晴")


def test_weather_unknown_city_returns_404() -> None:
    r = client.get("/weather/火星")
    assert r.status_code == 404
    assert "未知城市" in r.json()["detail"]


def test_list_cities_sorted() -> None:
    r = client.get("/cities")
    assert r.status_code == 200
    assert r.json()["cities"] == ["上海", "北京", "深圳"]


def test_search_weather_partial_match() -> None:
    r = client.get("/search", params={"q": "海"})
    assert r.status_code == 200
    cities = [row["city"] for row in r.json()]
    assert cities == ["上海"]

"""最小 FastAPI 天气 API（阶段 22，内存数据）。"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="阶段 22 天气工具", version="0.1.0")
_DB: dict[str, str] = {
    "上海": "晴 22°C",
    "北京": "多云 18°C",
    "深圳": "阵雨 26°C",
}


class WeatherOut(BaseModel):
    city: str
    summary: str


class CityList(BaseModel):
    cities: list[str] = Field(default_factory=list)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/cities", response_model=CityList)
def list_cities() -> CityList:
    return CityList(cities=sorted(_DB.keys()))


@app.get("/weather/{city}", response_model=WeatherOut)
def weather(city: str) -> WeatherOut:
    summary = _DB.get(city)
    if summary is None:
        raise HTTPException(status_code=404, detail=f"未知城市: {city}")
    return WeatherOut(city=city, summary=summary)


@app.get("/search", response_model=list[WeatherOut])
def search_weather(q: str = Query("", min_length=0)) -> list[WeatherOut]:
    needle = q.strip()
    if not needle:
        return []
    hits = [WeatherOut(city=c, summary=s) for c, s in _DB.items() if needle in c]
    return sorted(hits, key=lambda item: item.city)

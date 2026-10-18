"""最小 FastAPI 天气 API（阶段 22，内存数据）。"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
_DB = {"上海": "晴 22°C", "北京": "多云 18°C"}


class WeatherOut(BaseModel):
    city: str
    summary: str


@app.get("/weather/{city}", response_model=WeatherOut)
def weather(city: str) -> WeatherOut:
    summary = _DB.get(city, "未知")
    return WeatherOut(city=city, summary=summary)

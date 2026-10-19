---
title: 22.3 测试 API
---

# 22.3 测试 API

> 前置：15. pytest、22.2 FastAPI · 约 35 分钟 · 官方对应：[FastAPI 测试](https://fastapi.tiangolo.com/tutorial/testing/) · 核对日期 2026-10-18

## 目标

- 用 **`TestClient`** 在进程内调用 ASGI 应用，不占用真实端口、不发外网请求。
- 断言 **HTTP 状态码** 与 **JSON 体** 字段；覆盖 happy path 与错误路径（422、404 等）。
- 把 API 测试与 CLI 测试类比：都是“调用边界 + 断言结构化输出”。
- 读懂阶段 22 项目 `test_app.py`，并能在本地扩展用例。
- 能区分集成测试（TestClient）与端到端测试（真实端口）的适用场景。

## 核心概念

### TestClient 模式（静态）

```python
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_weather():
    r = client.get("/weather/上海")
    assert r.status_code == 200
    data = r.json()
    assert data["city"] == "上海"
```

### 课内可运行：模拟响应对象

不依赖 FastAPI，先练断言结构：

```python run
class FakeResponse:
    def __init__(self, status: int, payload: dict):
        self.status_code = status
        self._payload = payload

    def json(self) -> dict:
        return self._payload

r = FakeResponse(200, {"city": "上海", "summary": "晴"})
assert r.status_code == 200
assert r.json()["summary"].startswith("晴")
```

### 422 校验错误

请求体或查询参数类型不对时，FastAPI 返回 422；课内用函数模拟：

```python run
def build_search_query(q: str, limit_raw: str) -> dict[str, str | int]:
    limit = int(limit_raw)
    if limit < 1:
        raise ValueError("too small")
    if limit > 100:
        raise ValueError("too large")
    return {"q": q.strip(), "limit": limit}


def fake_get(path: str, params: dict[str, str | int]) -> dict[str, object]:
    return {"path": path, "params": params, "status": 200}


query = build_search_query("  weather  ", "25")
response = fake_get("/search", query)
print("构造 query", query)
print("假 TestClient 响应", response)
assert response["params"]["limit"] == 25
```

测试里先单独验证「查询字符串 → 业务参数字典」，再喂给假 GET；输出包含路径与 status，强调 **422 之前参数解析也可单测**。

```python run raises=ValueError
def parse_limit(raw: str) -> int:
    print("收到 limit 原始值", repr(raw))
    try:
        value = int(raw)
    except ValueError:
        print("不是十进制整数")
        raise ValueError("invalid")
    if value < 1:
        print("数值过小", value)
        raise ValueError("too small")
    return value


for bad in ("abc", "-3", "0"):
    print("--- 尝试", bad, "---")
    try:
        parse_limit(bad)
    except ValueError as err:
        print("捕获", err)
        if bad == "abc":
            raise
```

只对 `"abc"` 让异常继续抛出以满足 `raises=`，前两例在块内捕获并打印错误消息，展示测试应断言**不同失败原因**（invalid vs too small）。

### 隔离外部依赖

测试不应打真实天气 API；阶段项目用 `_DB` 字典，测试只验证路由与序列化。若将来注入 HTTP 客户端，用 `app.dependency_overrides` 替换（FastAPI 文档模式）。

```python run
def lookup(city: str, db: dict[str, str]) -> str:
    return db.get(city, "未知")

db = {"上海": "晴 22°C"}
assert lookup("上海", db).startswith("晴")
assert lookup("广州", db) == "未知"
```


## 易错点

- **忘记 `uv sync --group web`**：`TestClient` 与 `fastapi` 在 `web` 组，CI 已装全组。
- **断言整个 JSON 对象**：摘要字符串可能变，用 `startswith` 或正则更稳（见仓库测试）。
- **在测试里 `uvicorn.run`**：慢且占端口；优先 `TestClient`。
- **共享可变全局 `_DB`**：用例之间若修改 `_DB` 会互相污染；每个测试用 fixture 拷贝或 monkeypatch。

## 对照

| 方式 | Python FastAPI | Node | Java |
|---|---|---|---|
| 进程内测 HTTP | `TestClient` | `supertest` | `MockMvc` |
| 启真实端口 | `uvicorn` 手工 | `listen(0)` | `@SpringBootTest` |
| 断言 JSON | `response.json()` | `res.body` | `jsonPath` |

## 读代码

仓库测试 [`test_app.py`](../../../examples/项目/22-天气工具API/test_app.py)：

```python
from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_weather() -> None:
    r = client.get("/weather/上海")
    assert r.status_code == 200
    assert r.json()["summary"].startswith("晴")
```

说明：

1. `TestClient(app)` 构造时导入 `app`，会执行 `app.py` 顶层（创建 `FastAPI()` 与 `_DB`）。
2. `client.get` 同步调用 ASGI 栈，返回 `Response`，与 `httpx` 接口相似。
3. 只断言 `summary` 前缀，不绑死温度数字，便于改 `_DB` 文案。
4. 可再加 `test_unknown_city`：`client.get("/weather/广州")` 断言 `summary == "未知"`。
5. 若路由写错路径，会得到 404，`status_code` 断言立刻失败。

运行：

```bash
uv sync --group web
uv run pytest examples/项目/22-天气工具API/test_app.py -q
```

全项目阶段测试：

```bash
uv run pytest examples/项目/22-天气工具API -q
```

## 练习

### 练习 1：断言状态码

```python exercise id=s22-l03-api
# --- starter ---
def ok(status: int) -> bool:
    return False
# --- solution ---
def ok(status: int) -> bool:
    return status == 200
# --- check ---
assert ok(200)
assert not ok(404)
```

### 练习 2：解析 JSON 字段

```python exercise id=s22-l03-parse
# --- starter ---
def city_from_payload(data: dict) -> str:
    return ""
# --- solution ---
def city_from_payload(data: dict) -> str:
    return str(data["city"])
# --- check ---
assert city_from_payload({"city": "上海", "summary": "晴"}) == "上海"
```

### CI 与依赖组

GitHub Actions 使用 `uv sync --all-groups`，因此 `web` 组在 CI 中可用。本地若只 `uv sync` 未装 FastAPI，`TestClient` 导入会失败——课文命令统一写 `uv sync --group web` 前缀，与 22.1、22.2 保持一致。

为 API 测试建 `client` fixture 可避免每个用例重复构造 `TestClient`。断言 JSON 时优先键存在性，再比具体文案，减少因文案微调导致的脆弱测试。

对 404 路由写负例：`client.get("/nope")` 断言 `status_code == 404`，防止路由表被误删。


## 小结

- `TestClient` 是阶段 22 的默认测试入口；快、无网络、可进 CI。
- 断言分层：先 `status_code`，再 JSON 字段；脆弱字符串用前缀匹配。
- 读 `test_app.py` 对照 `app.py` 路由与 `_DB` 行为。
- 命令：`uv run pytest examples/项目/22-天气工具API/test_app.py -q`。
- `response.headers` 可断言 `content-type`。
- 表单与 JSON body 测法不同，天气 API 仅 JSON GET。
- 异步路由仍用同步 `TestClient`，内部事件循环由框架处理。
- 失败时打印 `response.text` 便于看校验错误详情。
- 夹具 `autouse` 可重置 `_DB`，避免测试顺序依赖。
- 与 15 课 pytest 习惯一致：一断言一事，命名说清场景。
- `pytest.raises` 可测异常路由，阶段项目暂用 200 默认值。
- 参数化 `@pytest.mark.parametrize` 可测多城市 URL。
- 测试文件与 `app.py` 同目录，导入路径保持扁平。
- Mock 上游天气 API 时 patch 函数而非 HTTP，除非测集成。
- 核对日期 2026-10-18：FastAPI TestClient 与 httpx 版本由 `uv.lock` 锁定。
- 失败用例保留 `response.json()` 打印，422 时 body 含字段级错误。

## 延伸阅读

- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

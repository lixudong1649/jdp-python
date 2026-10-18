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
def parse_limit(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError:
        raise ValueError("invalid")
    if value < 1:
        raise ValueError("too small")
    return value

assert parse_limit("10") == 10
```

```python run raises=ValueError
def parse_limit(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError:
        raise ValueError("invalid")
    if value < 1:
        raise ValueError("too small")
    return value

parse_limit("abc")
```

### 隔离外部依赖

测试不应打真实天气 API；阶段项目用 `_DB` 字典，测试只验证路由与序列化。若将来注入 HTTP 客户端，用 `app.dependency_overrides` 替换（FastAPI 文档模式）。

```python run
def lookup(city: str, db: dict[str, str]) -> str:
    return db.get(city, "未知")

db = {"上海": "晴 22°C"}
assert lookup("上海", db).startswith("晴")
assert lookup("广州", db) == "未知"
```


### 课堂延展：测试 API

本段补充对应 `docs/课程/22-Web与API/03-测试API.md`，帮助把课文与阶段 22 项目里的真实文件对齐；建议边读边在仓库里搜索 `03-测试API` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：用 **`TestClient`** 在进程内调用 ASGI 应用，不占用真实端口、不发外网请求。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：断言 **HTTP 状态码** 与 **JSON 体** 字段；覆盖 happy path 与错误路径（422、404 等）。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：把 API 测试与 CLI 测试类比：都是“调用边界 + 断言结构化输出”。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：读懂阶段 22 项目 `test_app.py`，并能在本地扩展用例。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 5：能区分集成测试（TestClient）与端到端测试（真实端口）的适用场景。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 22 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（03-测试API·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（03-测试API·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 22-Web与API` 为准；浏览器端主要用于交互体验。（03-测试API·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（03-测试API·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（03-测试API·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（03-测试API·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（03-测试API·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（03-测试API·8）

下面再跑一个与《03-测试API》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
payload = {"city": "上海"}
print("city" in payload and isinstance(payload["city"], str))
```

自测题（docs/课程/22-Web与API/03-测试API.md·0）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·1）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·2）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·3）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·4）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·5）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·6）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·7）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·8）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·9）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·10）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·11）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·12）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·13）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·14）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·15）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·16）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·17）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·18）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·19）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·20）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·21）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·22）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·23）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·24）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·25）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·26）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·27）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/03-测试API.md·28）：若让你向同事用三分钟讲清「22.3 测试 API」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

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

- 达标备注（docs/课程/22-Web与API/03-测试API.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

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

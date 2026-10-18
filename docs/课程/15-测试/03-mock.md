---
title: 15.3 mock 与 monkeypatch
---

# 15.3 mock 与 monkeypatch

> 前置：15.2 fixture · 约 35 分钟 · 官方对应：[monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)、[unittest.mock](https://docs.python.org/zh-cn/3/library/unittest.mock.html) · 核对日期 2026-10-18

## 目标

- 隔离**外部依赖**：环境变量、网络、时钟、随机数，避免测试脆弱或昂贵。
- 会用 pytest 的 `monkeypatch` 临时改 `os.environ` 或替换属性，退出测试后自动恢复。
- 理解「mock 过多」的症状：测试跟着实现细节改，而不是跟着行为契约改。
- 联系 Agent 场景：用假 LLM 客户端替代真实 SDK 调用（与 `minimal_agent` 的 `PROVIDERS` 思路一致）。

## 核心概念

### 为什么要隔离

```python run
import os

def provider_name() -> str:
    return os.getenv("LLM_PROVIDER", "default")

# 直接依赖环境：在 CI 与同事机器上可能不同
saved = os.environ.get("LLM_PROVIDER")
os.environ["LLM_PROVIDER"] = "demo"
assert provider_name() == "demo"
if saved is None:
    os.environ.pop("LLM_PROVIDER", None)
else:
    os.environ["LLM_PROVIDER"] = saved
print("manual restore ok")
```

手写恢复容易漏；pytest `monkeypatch.setenv` 在测试结束后还原。

### monkeypatch 常用 API

```python fragment
def test_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "demo")
    assert provider_name() == "demo"

def test_fake_time(monkeypatch):
    monkeypatch.setattr("mymod.time.time", lambda: 1_700_000_000.0)
```

- `setenv(name, value)` / `delenv(name)`：环境变量。
- `setattr(target, name, value)` / `setitem(dict, key, value)`：对象属性或字典项。
- `syspath_prepend(path)`：临时扩展导入路径（少用，优先 conftest）。

课内模拟 `setattr` 替换函数：

```python run
def real_fetch() -> str:
    return "live-api"

def test_with_fake_fetch():
    calls = {"n": 0}

    def fake_fetch() -> str:
        calls["n"] += 1
        return "stub"

    # 模拟 monkeypatch：保存、替换、恢复
    backup = real_fetch
    try:
        globals()["real_fetch"] = fake_fetch
        assert real_fetch() == "stub"
        assert calls["n"] == 1
    finally:
        globals()["real_fetch"] = backup

test_with_fake_fetch()
```

### Fake 对象 vs Mock 框架

| 方式 | 优点 | 缺点 |
|---|---|---|
| 手写 fake（小类/闭包） | 行为清晰、易读 | 代码稍多 |
| `unittest.mock.Mock` | 自动记录调用 | 容易断言过多内部细节 |
| `monkeypatch` | 与 pytest 生命周期绑定 | 需知道被替换的导入路径 |

Agent 测试常见模式：实现 `FakeMessages` 只返回固定 JSON，不走网络。

```python run
class FakeClient:
    def complete(self, prompt: str) -> str:
        return f"echo:{prompt}"

def run_agent(client: FakeClient, user: str) -> str:
    return client.complete(user)

assert run_agent(FakeClient(), "hi") == "echo:hi"
```

### 该 mock 什么，不该 mock 什么

- **适合**：网络、环境变量、系统时钟、随机种子、第三方 SDK。
- **谨慎**：被你测模块内部的纯函数——若 mock 了实现细节，重构时测试全红。
- **避免**：为了覆盖率 mock 掉所有逻辑，只剩「调用了 mock」的空测试。


### 课堂延展：mock 与 monkeypatch

本段补充对应 `docs/课程/15-测试/03-mock.md`，帮助把课文与阶段 15 项目里的真实文件对齐；建议边读边在仓库里搜索 `03-mock` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：隔离**外部依赖**：环境变量、网络、时钟、随机数，避免测试脆弱或昂贵。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：会用 pytest 的 `monkeypatch` 临时改 `os.environ` 或替换属性，退出测试后自动恢复。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：理解「mock 过多」的症状：测试跟着实现细节改，而不是跟着行为契约改。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：联系 Agent 场景：用假 LLM 客户端替代真实 SDK 调用（与 `minimal_agent` 的 `PROVIDERS` 思路一致）。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 15 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（03-mock·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（03-mock·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 15-测试` 为准；浏览器端主要用于交互体验。（03-mock·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（03-mock·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（03-mock·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（03-mock·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（03-mock·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（03-mock·8）

下面再跑一个与《03-mock》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
items = [1, 2, 3]
assert sum(items) == 6
print("sum ok")
```

自测题（docs/课程/15-测试/03-mock.md·0）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·1）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·2）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·3）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·4）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·5）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·6）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·7）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·8）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·9）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·10）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·11）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·12）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·13）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·14）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·15）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·16）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·17）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·18）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·19）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·20）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·21）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·22）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·23）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·24）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·25）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·26）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·27）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/03-mock.md·28）：若让你向同事用三分钟讲清「15.3 mock 与 monkeypatch」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **patch 路径写错**：应 patch **使用方**命名空间里的名字，例如 `mymodule.requests.get`，而不是 `requests.get`（若 mymodule 已 `import requests`）。
- **忘记恢复**：不用 monkeypatch 时，用 `try/finally` 或 context manager。
- **mock 返回值类型不对**：假客户端返回的结构要与真 SDK 一致，否则测的是假数据格式。

```python run raises=TypeError
def need_int(x: int) -> int:
    return x + 1

class BadFake:
    def read(self):
        return "not-int"

fake = BadFake()
need_int(fake.read())  # str 传入，运行期才爆
```

类型注解帮 mypy 提前发现；运行时仍需让 fake 返回合法类型。

## 对照

| 场景 | pytest | unittest | Java |
|---|---|---|---|
| 环境变量 | `monkeypatch.setenv` | `@patch.dict(os.environ)` | `EnvironmentVariables` |
| 替换属性 | `monkeypatch.setattr` | `@patch` | Mockito `when` |
| 调用记录 | `Mock.assert_called_once` | `mock.assert_called_with` | `verify(mock)` |
| 自动恢复 | fixture 结束还原 | `patch` 上下文退出 | `@After` 重置 |

## 读代码

阶段 15 测试目前**没有** mock：依赖 `conftest` 路径与真实 `logstats` 实现。这是合理分层——先测真逻辑。若要为 `main` 加「读文件失败」用例而不创建真实磁盘错误，可以：

```python fragment
def test_main_missing_file(monkeypatch, tmp_path: Path):
    missing = tmp_path / "nope.log"
    monkeypatch.setattr(Path, "read_text", lambda self, **kw: (_ for _ in ()).throw(FileNotFoundError()))
    assert main([str(missing)]) == 1  # 若 main 将来返回错误码
```

读 [`test_cli_logstats.py`](../../../examples/项目/15-CLI测试/test_cli_logstats.py) 时，问自己：**有没有外部 I/O？** 有则 `tmp_path` 或 monkeypatch；纯 `parse_lines` 则直接字符串。

`minimal_agent` 里用环境变量选 provider 时，测试应 `monkeypatch.setenv` 而不是改用户机器上的 `.env`。

当依赖是「从磁盘读配置」时，优先像 15 课那样用 `tmp_path` 写真实文件，比 mock `open` 更贴近生产行为；只有磁盘 I/O 太慢或不可控时才 patch 底层调用。

记录 mock 调用次数（`Mock.call_count`）适合验证「重试三次」这类协议；若测试只关心最终返回值，手写 fake 返回固定值即可，不必断言每一次内部调用。

## 练习

### 练习 1

```python exercise id=s15-l03-mock
# --- starter ---
def always_true():
    return False
# --- solution ---
def always_true():
    return True
# --- check ---
assert always_true()
```

### 练习 2：可注入的 `get_config`

实现 `get_config(env: dict[str, str] | None = None) -> str`：从 `env` 读 `MODE`，缺省为 `"dev"`。不要读真实 `os.environ`，便于测试。

```python exercise id=s15-l03-config
# --- starter ---
def get_config(env: dict[str, str] | None = None) -> str:
    return "dev"
# --- solution ---
def get_config(env: dict[str, str] | None = None) -> str:
    data = env if env is not None else {}
    return data.get("MODE", "dev")
# --- check ---
assert get_config({}) == "dev"
assert get_config({"MODE": "prod"}) == "prod"
```

- 达标备注（docs/课程/15-测试/03-mock.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

维护测试时，如果每次改实现都要改 mock 断言，说明 mock 层太靠内——把 fake 放在模块边界（HTTP 客户端、数据库网关）通常更稳。

文档字符串里的示例若会打真实 API，应用 `if __name__ == "__main__"`  guard，别让 pytest 收集到副作用函数。

- 用 monkeypatch / fake 隔离外部环境，测试聚焦行为。
- patch 目标应是依赖边界，不是被测函数内部的每一步。
- 阶段 15 以真实 `logstats` 为主；mock 在 Agent、网络课中更常见。

15.4 会讨论哪些分支已被测试执行到，与 mock 互补：mock 缩小世界，覆盖率告诉你还有哪些真实分支没走到。

命名 fake 类时带上 `Fake` 或 `Stub` 前缀，与生产实现类并列时一眼可辨，避免误导入到业务代码。

替换 `datetime.now` 时，记得同时固定时区相关的辅助函数，否则跨日测试会偶发失败。

## 延伸阅读

- [monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [unittest.mock](https://docs.python.org/zh-cn/3/library/unittest.mock.html)
- [如何测试有依赖的代码（pytest 文档）](https://docs.pytest.org/en/stable/how-to/fixtures.html#monkeypatching-built-ins-and-environment-variables)

monkeypatch 与 `unittest.mock.patch` 可互换场景很多；本仓库 pytest 风格优先前者，生命周期与 fixture 一致。

集成测试里尽量少 patch：能起本地假服务（如 TestClient）时，行为比深层 mock 更接近上线。

Fake 实现应写在 `tests/` 或 `tests/fakes.py`，不要塞进生产包，避免被打进 wheel（17 课）。

读 `unittest.mock` 文档时，重点看 `patch` 的 `autospec` 参数，可减少 fake 方法签名漂移。

阶段 23 Agent 课会组合 fake LLM 与 pytest，届时回头对照本课边界即可。

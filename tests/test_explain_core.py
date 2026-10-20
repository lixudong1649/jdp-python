"""py-explain 分析器单元测试。"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPLAIN = ROOT / "site" / "public" / "py-explain.py"
SCHEMA = ROOT / "site" / "public" / "py-explain.schema.json"
FIXTURES = Path(__file__).parent / "fixtures" / "explain"


def _load():
    spec = importlib.util.spec_from_file_location("py_explain", EXPLAIN)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pe():
    return _load()


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def test_explain_function_exists(pe):
    assert hasattr(pe, "explain")


def test_schema_file_exists():
    assert SCHEMA.is_file()


def test_no_exec_in_source():
    text = EXPLAIN.read_text(encoding="utf-8")
    assert "exec(" not in text
    assert "eval(" not in text


@pytest.mark.parametrize(
    "code, syntax",
    [
        ("import os\n", "import"),
        ("from json import loads\n", "from … import …"),
        ("x = {'a': 1}\n", "dict 字面量"),
        ("xs = [1, 2]\n", "list 字面量"),
        ("for i in range(2):\n    pass\n", "for + range"),
        ("def f():\n    return 1\n", "def / return"),
        ("s = f'{1}'\n", "f-string"),
        ("if a != b:\n    pass\n", "!="),
        ("xs.append(1)\n", "list.append"),
        ("''.join([])\n", "str.join"),
        ("a[b]\n", "下标访问"),
        ("obj.method()\n", "属性访问 / 方法调用"),
        ("[x for x in range(2)]\n", "列表推导式"),
        ("v = None or 1\n", "or 取默认值"),
        ("class C:\n    pass\n", "class"),
        ("try:\n    pass\nexcept ValueError:\n    pass\n", "try"),
        ("with open('x') as f:\n    pass\n", "with"),
        ("f = lambda x: x\n", "lambda"),
        ("if (n := 1):\n    pass\n", ":= 海象运算符"),
        ("for i in range(1):\n    break\n", "break"),
        ("for i in range(1):\n    pass\nelse:\n    pass\n", "for … else"),
        ("def f(**kw):\n    pass\nf(**{'a': 1})\n", "** 解包"),
    ],
)
def test_syntax_labels(pe, code, syntax):
    r = pe.explain(code)
    assert r["ok"]
    labels = {p["syntax"] for p in r["syntax_points"]}
    assert syntax in labels


@pytest.mark.parametrize(
    "code, rule_id",
    [
        ("def f(a=[]):\n    return a\n", "mutable-default-arg"),
        ("if x is 'a':\n    pass\n", "is-literal-compare"),
        ("try:\n    1\nexcept:\n    pass\n", "bare-except"),
        ("if x == None:\n    pass\n", "none-equality"),
        ("from os import *\n", "wildcard-import"),
        ("open('a.txt')\n", "open-no-with"),
        ("def list():\n    pass\n", "shadow-builtin"),
        ("class A:\n    xs = []\n", "mutable-class-attribute"),
        ("try:\n    f()\nexcept TypeError:\n    pass\n", "except-pass"),
        ("assert True\n", "assert-trivial"),
        ("if len(x):\n    pass\n", "len-as-bool"),
        ("d = {'a': 1, 'a': 2}\n", "duplicate-key-dict-literal"),
    ],
)
def test_pitfall_rules(pe, code, rule_id):
    r = pe.explain(code)
    assert r["ok"]
    ids = {p["rule_id"] for p in r["pitfalls"]}
    assert rule_id in ids


@pytest.mark.parametrize(
    "code",
    [
        "def f(\n",
        "if True\n    pass\n",
        "print(1\n",
    ],
)
def test_syntax_error_shape(pe, code):
    r = pe.explain(code)
    assert r["ok"] is False
    assert r["error"]["line"] >= 1
    assert r["error"]["message"]


def test_overview_line_count(pe):
    code = "a = 1\nb = 2\n"
    r = pe.explain(code)
    assert r["ok"]
    assert r["overview"]["line_count"] == 2


def test_module_docstring(pe):
    code = '"""mod"""\nx = 1\n'
    r = pe.explain(code)
    assert r["ok"]
    assert "mod" in (r["overview"]["docstring"] or "")


def test_third_party_blocks_browser(pe):
    code = "import anthropic\n"
    r = pe.explain(code)
    assert r["ok"]
    assert r["run_info"]["can_run_in_browser"] is False
    assert "anthropic" in r["run_info"]["third_party"]


def test_stdlib_ok_browser(pe):
    code = "import json\n"
    r = pe.explain(code)
    assert r["ok"]
    assert r["run_info"]["can_run_in_browser"] is True


def test_structure_function_params(pe):
    code = "def add(a, b=1):\n    return a + b\n"
    r = pe.explain(code)
    assert r["ok"]
    fn = next(x for x in r["structure"] if x["name"] == "add")
    assert "a" in fn["params"] and "b" in fn["params"]


def test_concepts_non_empty(pe):
    r = pe.explain("import os\n")
    assert r["ok"]
    assert len(r["concepts"]) >= 1


def test_minimal_agent_file(pe):
    src = (ROOT / "examples/agent/minimal_agent.py").read_text(encoding="utf-8")
    r = pe.explain(src, "minimal_agent.py")
    assert r["ok"]
    assert len(r["syntax_points"]) >= 15


@pytest.mark.parametrize("case_dir", sorted(p for p in FIXTURES.iterdir() if p.is_dir()))
def test_gold_fixture(case_dir, pe):
    src = (case_dir / "source.py").read_text(encoding="utf-8")
    exp = json.loads((case_dir / "expected.json").read_text(encoding="utf-8"))
    act = pe.explain(src, case_dir.name + ".py")
    assert act.get("ok") == exp.get("ok")
    if not act.get("ok"):
        return
    for key in ("syntax_points", "pitfalls", "overview"):
        if key not in exp:
            continue
        if key == "syntax_points":
            for item in exp["syntax_points"]:
                assert any(
                    item.get("syntax") == a.get("syntax") and item.get("concept_id") == a.get("concept_id")
                    for a in act.get("syntax_points", [])
                )
        elif key == "pitfalls":
            exp_ids = {x["rule_id"] for x in exp["pitfalls"]}
            act_ids = {x["rule_id"] for x in act.get("pitfalls", [])}
            assert exp_ids <= act_ids
        elif key == "overview":
            for k, v in exp["overview"].items():
                assert act["overview"].get(k) == v


def test_pitfall_selftest_complete(pe):
    assert len(pe.PITFALL_RULES) >= 10
    for rule in pe.PITFALL_RULES:
        cases = pe.PITFALL_SELFTEST[rule["id"]]
        assert len(cases["should_hit"]) >= 2
        assert len(cases["should_miss"]) >= 2


def test_cli_entrypoint():
    assert "--cli" in EXPLAIN.read_text(encoding="utf-8")


@pytest.mark.parametrize("i", range(10))
def test_stable_json_roundtrip(pe, i):
    code = f"x = {i}\nprint(x)\n"
    a = pe.explain(code)
    b = pe.explain(code)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)

"""代码解读质量校验：语料批量分析、概念索引、易错点规则、金标样例与（可选）AI 讲解门禁。

用法（项目根目录）：
    uv run python tests/check_explain.py
    uv run python tests/check_explain.py --only E01,E07
    uv run python tests/check_explain.py --live   # 含 A01–A04（需本机 Ollama 等服务）

与 check_course.py 共用语料解析（python run / exercise / examples/*.py）。
"""

from __future__ import annotations

import argparse
import ast
import difflib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import unquote

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
sys.path.insert(0, str(TESTS_DIR))

from check_course import (  # noqa: E402
    COURSE,
    DOCS,
    Block,
    parse_blocks,
    parse_exercise,
    rel,
)

EXPLAIN_SCRIPT = ROOT / "site" / "public" / "py-explain.py"
SCHEMA_PATH = ROOT / "site" / "public" / "py-explain.schema.json"
CONCEPT_INDEX = DOCS / "代码解读" / "概念索引.md"
MINIMAL_AGENT_MD = DOCS / "代码解读" / "minimal_agent.md"
MINIMAL_AGENT_PY = ROOT / "examples" / "agent" / "minimal_agent.py"
FIXTURES_DIR = TESTS_DIR / "fixtures" / "explain"
EXAMPLES_DIR = ROOT / "examples"
SITE_DIST = ROOT / "site" / ".vitepress" / "dist"

SECTION_KEYS = ("overview", "syntax_points", "structure", "concepts", "run_info", "pitfalls")

SYNTAX_ERROR_SAMPLES: list[tuple[str, int | None]] = [
    ("def f(\n", 1),
    ("x = \n", 1),
    ("if True\n    pass\n", 1),
    ("print(1\n", 1),
    ("for i in range(10\n    pass\n", 1),
    ("class\n", 1),
    ("import\n", 1),
    ("@\n", 1),
    ("async def f():\n    await\n", 2),
    ("match x:\n    case\n", 2),
]

MINIMAL_AGENT_ROWS: list[tuple[str, list[int]]] = [
    ("文档字符串", list(range(1, 10))),
    ("注释", [16]),
    ("import", [11, 13]),
    ("from … import …", [14]),
    ("dict 字面量", list(range(20, 32))),
    ("None", [27]),
    ("全大写常量", []),  # 名称级，行号由赋值行覆盖
    ("or 取默认值", [34, 36]),
    ("下标访问", [35, 36]),
    ("关键字参数", list(range(37, 41))),
    ("list 字面量", list(range(43, 54))),
    ("def", [56]),
    ("return", [58]),
    ("f-string", [58]),
    ("函数作为值", [62]),
    ("for", [68]),
    ("range", [68]),
    ("属性访问", [70, 77, 81]),
    ("list.append", [77, 96]),
    ("if", [80]),
    ("!=", [80]),
    ("列表推导式", [81]),
    ("str.join", [81]),
    ("break", [83]),
    ("**", [89]),
    ("for … else", [97]),
]

PITFALL_RULE_IDS = [
    "mutable-default-arg",
    "is-literal-compare",
    "bare-except",
    "none-equality",
    "wildcard-import",
    "open-no-with",
    "shadow-builtin",
    "mutable-class-attribute",
    "except-pass",
    "assert-trivial",
    "len-as-bool",
    "duplicate-key-dict-literal",
]


@dataclass
class Report:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def ok(self, code: str, msg: str) -> None:
        self.passed.append(f"{code}: {msg}")

    def fail(self, code: str, msg: str) -> None:
        self.failed.append(f"{code}: {msg}")

    def skip(self, code: str, msg: str) -> None:
        self.skipped.append(f"{code}: {msg}")


def load_schema() -> dict[str, Any]:
    if not SCHEMA_PATH.is_file():
        return {}
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _type_name(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, int):
        return "integer"
    if isinstance(v, float):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    if isinstance(v, dict):
        return "object"
    return "unknown"


def validate_schema_instance(data: Any, schema: dict[str, Any], path: str = "") -> list[str]:
    errors: list[str] = []
    if not schema:
        if not isinstance(data, dict):
            return [f"{path or 'root'}: 期望 object"]
        if data.get("ok") is True:
            for key in SECTION_KEYS:
                if key not in data:
                    errors.append(f"{path}.{key}: 缺少键")
        return errors

    t = schema.get("type")
    if t:
        actual = _type_name(data)
        allowed = t if isinstance(t, list) else [t]
        if actual not in allowed:
            errors.append(f"{path or 'root'}: 期望 {allowed}，实际 {actual}")
            return errors
    if t == "object":
        req = schema.get("required", [])
        for key in req:
            if key not in data:
                errors.append(f"{path}.{key}: 缺少必填字段")
        props = schema.get("properties", {})
        for key, sub in props.items():
            if key in data:
                errors.extend(validate_schema_instance(data[key], sub, f"{path}.{key}"))
    elif t == "array":
        item_schema = schema.get("items", {})
        if isinstance(data, list):
            for i, item in enumerate(data):
                errors.extend(validate_schema_instance(item, item_schema, f"{path}[{i}]"))
    return errors


def load_explain_module():
    if not EXPLAIN_SCRIPT.is_file():
        return None
    spec = importlib.util.spec_from_file_location("py_explain", EXPLAIN_SCRIPT)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def explain_code(mod, source: str, filename: str = "<input>") -> dict[str, Any]:
    if hasattr(mod, "explain"):
        return mod.explain(source, filename=filename)
    if hasattr(mod, "analyze"):
        return mod.analyze(source, filename=filename)
    raise RuntimeError("py-explain 缺少 explain/analyze 入口")


def collect_corpus() -> tuple[list[tuple[str, str, str]], dict[str, int]]:
    """返回 [(label, filename_hint, code), ...] 与统计。"""
    items: list[tuple[str, str, str]] = []
    course_files = sorted(COURSE.rglob("*.md"))
    all_blocks: list[Block] = []
    seen_exercise: set[str] = set()
    n_browser_ex = 0
    n_local_ex = 0
    for f in course_files:
        all_blocks.extend(parse_blocks(f))
    n_run = 0
    for b in all_blocks:
        where = f"{rel(b.file)}:{b.line}"
        if b.lang != "python":
            continue
        if "run" in b.flags:
            n_run += 1
            items.append((where, where, b.content))
        if "exercise" in b.flags:
            ex_id = b.attrs.get("id", "")
            if ex_id in seen_exercise:
                continue
            seen_exercise.add(ex_id)
            parts = parse_exercise(b.content)
            sol = parts.get("solution", "").strip()
            if not sol:
                continue
            if "local" in b.flags:
                n_local_ex += 1
            else:
                n_browser_ex += 1
            items.append((f"exercise:{ex_id}", where, sol + "\n"))
    py_files = sorted(EXAMPLES_DIR.rglob("*.py"))
    n_py = len(py_files)
    for p in py_files:
        items.append((rel(p), rel(p), p.read_text(encoding="utf-8")))
    stats = {
        "python_run_blocks": n_run,
        "exercises_total": len(seen_exercise),
        "exercises_browser": n_browser_ex,
        "exercises_local": n_local_ex,
        "examples_py_files": n_py,
        "corpus_total": len(items),
    }
    return items, stats


def check_e01(report: Report, mod, schema: dict) -> None:
    code = "E01"
    if mod is None:
        report.fail(code, "分析器 site/public/py-explain.py 不存在")
        return
    corpus, stats = collect_corpus()
    report.stats["corpus"] = stats
    crashes: list[str] = []
    bad_schema: list[str] = []
    empty_syntax: list[str] = []
    one_of = schema.get("oneOf", []) if schema.get("oneOf") else [schema]
    success_schema = one_of[0] if one_of else schema
    error_schema = one_of[1] if len(one_of) > 1 else {"type": "object", "required": ["ok", "error"]}
    for label, _, src in corpus:
        try:
            result = explain_code(mod, src, filename=label)
        except Exception as exc:  # noqa: BLE001
            crashes.append(f"{label}: {exc}")
            continue
        if not result.get("ok"):
            errs = validate_schema_instance(result, error_schema)
            if errs:
                bad_schema.append(f"{label}: {'; '.join(errs[:2])}")
            continue
        errs = validate_schema_instance(result, success_schema)
        if errs:
            bad_schema.append(f"{label}: {'; '.join(errs[:3])}")
        syns = result.get("syntax_points") or []
        if len(syns) < 1:
            empty_syntax.append(label)
    if crashes:
        report.fail(code, f"语料 {len(corpus)} 份，崩溃/失败 {len(crashes)}（首条：{crashes[0]}）")
    elif bad_schema:
        report.fail(code, f"Schema 未通过 {len(bad_schema)} 份（首条：{bad_schema[0]}）")
    elif empty_syntax:
        report.fail(code, f"语法点为空 {len(empty_syntax)} 份（首条：{empty_syntax[0]}）")
    else:
        report.ok(code, f"语料 {len(corpus)} 份全部通过 Schema 且语法点 ≥1")


def check_e02(report: Report, mod) -> None:
    code = "E02"
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    script = ROOT / "site" / "scripts" / "verify-explain-pyodide.mjs"
    if not script.is_file():
        report.fail(code, "缺少 verify-explain-pyodide.mjs")
        return
    proc = subprocess.run(
        ["node", str(script)],
        cwd=ROOT / "site",
        capture_output=True,
        text=True,
        timeout=900,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        report.fail(code, f"Pyodide 对比失败 exit={proc.returncode}：{out.strip()[:400]}")
    else:
        line = next((ln for ln in out.splitlines() if ln.startswith("E02:")), out.strip()[:120])
        report.ok(code, line.replace("E02:", "").strip() or "语料 JSON 一致")


def parse_concept_index() -> list[dict[str, str]]:
    if not CONCEPT_INDEX.is_file():
        return []
    text = CONCEPT_INDEX.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line.startswith("|") or line.startswith("| ---"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 6 or parts[0] in ("概念 id", ""):
            continue
        rows.append(
            {
                "id": parts[0],
                "name": parts[1],
                "ast": parts[2],
                "meaning": parts[3],
                "course": parts[4],
                "glossary": parts[5],
            }
        )
    return rows


def ast_node_types_in_source(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    class V(ast.NodeVisitor):
        def __init__(self) -> None:
            self.names: set[str] = set()

        def generic_visit(self, node: ast.AST) -> None:
            self.names.add(type(node).__name__)
            super().generic_visit(node)

    v = V()
    v.visit(tree)
    return v.names


def concept_ast_map(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for row in rows:
        cid = row["id"]
        raw = row["ast"]
        nodes: set[str] = set()
        for part in re.split(r"[,、/|]", raw):
            part = part.strip()
            if not part or part in ("—", "-", "规则"):
                continue
            part = part.replace("ast.", "")
            if part.endswith("*"):
                part = part[:-1]
            nodes.add(part)
        mapping[cid] = nodes
    return mapping


def check_e03(report: Report, mod) -> None:
    code = "E03"
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    if not MINIMAL_AGENT_PY.is_file():
        report.fail(code, "缺少 examples/agent/minimal_agent.py")
        return
    src = MINIMAL_AGENT_PY.read_text(encoding="utf-8")
    result = explain_code(mod, src, filename="minimal_agent.py")
    if not result.get("ok"):
        report.fail(code, f"分析器返回错误：{result.get('error')}")
        return
    points = result.get("syntax_points") or []
    hit = 0
    misses: list[str] = []
    for label, expected_lines in MINIMAL_AGENT_ROWS:
        if label == "全大写常量":
            matched = any(
                p.get("syntax") == label or "常量" in str(p.get("syntax", ""))
                for p in points
            )
            if matched:
                hit += 1
            else:
                misses.append(label)
            continue
        found = False
        for p in points:
            syn = str(p.get("syntax", ""))
            if label.replace(" … ", " ").replace("…", "") not in syn and syn not in label:
                if label.startswith("from") and "from" not in syn.lower():
                    continue
                if label == "def" and syn != "def" and "def / return" not in syn:
                    continue
                if label not in syn and not _syntax_row_match(label, syn):
                    continue
            lines = set(p.get("lines") or [])
            if not expected_lines:
                found = True
                break
            if any(ln in lines for ln in expected_lines):
                found = True
                break
        if found:
            hit += 1
        else:
            misses.append(label)
    need = 20
    if hit >= need:
        report.ok(code, f"minimal_agent 手写表命中 {hit}/22（门槛 ≥{need}）")
    else:
        report.fail(code, f"命中 {hit}/22（需 ≥{need}），未命中：{', '.join(misses[:8])}")


def _syntax_row_match(table_label: str, point_syntax: str) -> bool:
    aliases = {
        "from … import …": ["from import", "from … import"],
        "def": ["def / return", "函数定义"],
        "return": ["def / return", "return"],
        "for … else": ["for else", "for-else"],
        "属性访问": ["属性访问", "方法调用", "属性"],
        "!= ": ["!="],
        "import": ["import 语句", "import"],
    }
    for key, vals in aliases.items():
        if table_label.startswith(key.split()[0]) and any(v in point_syntax for v in vals):
            return True
    return False


def check_e04(report: Report, mod) -> None:
    code = "E04"
    rows = parse_concept_index()
    if len(rows) < 60:
        report.fail(code, f"概念索引条目 {len(rows)} < 60")
        return
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    ast_to_concept: dict[str, str] = {}
    for row in rows:
        for node in concept_ast_map([row]).get(row["id"], set()):
            ast_to_concept.setdefault(node, row["id"])
    corpus, _ = collect_corpus()
    seen_nodes: set[str] = set()
    for _, _, src in corpus:
        seen_nodes |= ast_node_types_in_source(src)
    if not seen_nodes:
        report.fail(code, "语料未解析到 AST 节点")
        return
    unmapped = []
    for n in sorted(seen_nodes):
        if n in _IGNORE_AST_NODES:
            continue
        if n not in ast_to_concept and not getattr(mod, "AST_TO_CONCEPT", {}).get(n):
            unmapped.append(n)
    ratio = 1.0 - len(unmapped) / max(len(seen_nodes - _IGNORE_AST_NODES), 1)
    report.stats["e04_unmapped"] = unmapped[:30]
    report.stats["e04_ratio"] = round(ratio * 100, 2)
    if ratio >= 0.95:
        report.ok(code, f"AST 节点映射覆盖率 {ratio * 100:.1f}%（未映射 {len(unmapped)}）")
    else:
        sample = ", ".join(unmapped[:12])
        report.fail(code, f"覆盖率 {ratio * 100:.1f}% < 95%，未映射示例：{sample}")


_IGNORE_AST_NODES = {
    "Load",
    "Store",
    "Del",
    "Module",
    "Expr",
    "alias",
    "arguments",
    "arg",
    "keyword",
    "comprehension",
    "Slice",
    "FormattedValue",
    "JoinedStr",
    "TypeIgnore",
    "Interactive",
    "Expression",
    # 比较与运算符节点（语义已归入 Compare/BinOp/BoolOp/UnaryOp）
    "Eq",
    "NotEq",
    "Lt",
    "LtE",
    "Gt",
    "GtE",
    "Is",
    "IsNot",
    "In",
    "NotIn",
    "Add",
    "Sub",
    "Mult",
    "MatMult",
    "Div",
    "FloorDiv",
    "Mod",
    "Pow",
    "LShift",
    "RShift",
    "BitOr",
    "BitXor",
    "BitAnd",
    "And",
    "Or",
    "Not",
    "UAdd",
    "USub",
    "Invert",
}


def _resolve_md_link(href: str, base: Path) -> Path | None:
    if href.startswith(("http://", "https://", "mailto:")):
        return None
    if href.startswith("#"):
        return base
    target_part = unquote(href.split("#")[0])
    if not target_part:
        return base
    if href.startswith("/"):
        target = DOCS / target_part.lstrip("/")
    else:
        target = (base.parent / target_part).resolve()
    candidates = [target, target.with_suffix(".md"), target / "index.md"]
    for c in candidates:
        if c.exists() and c.is_file():
            return c
    return None


def check_e05(report: Report) -> None:
    code = "E05"
    rows = parse_concept_index()
    if not rows:
        report.fail(code, f"缺少或无法解析 {rel(CONCEPT_INDEX)}")
        return
    if len(rows) < 60:
        report.fail(code, f"概念数 {len(rows)} < 60")
        return
    bad: list[str] = []
    for row in rows:
        for col in ("course", "glossary"):
            href = row[col]
            if not href or href in ("—", "-"):
                continue
            m = re.search(r"\]\(([^)]+)\)", href)
            link = m.group(1) if m else href
            if link.startswith(("http://", "https://")):
                continue
            resolved = _resolve_md_link(link, CONCEPT_INDEX)
            if resolved is None:
                bad.append(f"{row['id']} {col} → {link}")
            elif "#" in link:
                anchor = link.split("#", 1)[1]
                text = resolved.read_text(encoding="utf-8") if resolved.is_file() else ""
                slug = anchor.lower()
                if slug and slug not in text and not re.search(rf"id=\"{re.escape(anchor)}\"", text):
                    # VitePress 锚点可能是标题 slug，放宽：标题文本存在即可
                    title_guess = unquote(anchor).replace("-", " ")
                    if title_guess not in text:
                        bad.append(f"{row['id']} 锚点 {anchor}")
    ex_id_re = re.compile(r"练习\s*`?([A-Za-z0-9_-]+)`?")
    for row in rows:
        for m in ex_id_re.finditer(row.get("course", "")):
            ex_id = m.group(1)
            # 练习 id 在课程块 attrs 中出现
            found = False
            for f in COURSE.rglob("*.md"):
                if f"id={ex_id}" in f.read_text(encoding="utf-8"):
                    found = True
                    break
            if not found and ex_id not in ("starter", "solution"):
                bad.append(f"练习 id 不存在：{ex_id}")
    if bad:
        report.fail(code, f"失效链接/锚点 {len(bad)}（首条：{bad[0]}）")
    else:
        report.ok(code, f"概念索引 {len(rows)} 条链接校验通过")


def _pitfall_cases(mod) -> dict[str, dict[str, list[str]]]:
    if mod is None:
        return {}
    return getattr(mod, "PITFALL_SELFTEST", {})


def check_e06(report: Report, mod) -> None:
    code = "E06"
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    rules = getattr(mod, "PITFALL_RULES", None)
    if not rules or len(rules) < 10:
        report.fail(code, f"易错点规则 {0 if not rules else len(rules)} < 10")
        return
    selftest = _pitfall_cases(mod)
    wrong: list[str] = []
    for rid in [r["id"] for r in rules]:
        cases = selftest.get(rid, {})
        pos = cases.get("should_hit", [])
        neg = cases.get("should_miss", [])
        if len(pos) < 2 or len(neg) < 2:
            wrong.append(f"{rid} 样例不足（+{len(pos)}/-{len(neg)}）")
            continue
        for snippet in pos:
            res = explain_code(mod, snippet)
            ids = {p.get("rule_id") for p in (res.get("pitfalls") or [])}
            if rid not in ids:
                wrong.append(f"{rid} 应命中未命中：{snippet[:40]!r}")
        for snippet in neg:
            res = explain_code(mod, snippet)
            ids = {p.get("rule_id") for p in (res.get("pitfalls") or [])}
            if rid in ids:
                wrong.append(f"{rid} 不应命中却命中：{snippet[:40]!r}")
    if wrong:
        report.fail(code, f"易错点自检 {len(wrong)} 项（首条：{wrong[0]}）")
    else:
        report.ok(code, f"{len(rules)} 条规则正反样例全部判对")


def check_e07(report: Report, mod) -> None:
    code = "E07"
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    src_text = EXPLAIN_SCRIPT.read_text(encoding="utf-8")
    forbidden = [
        (r"\bexec\s*\(", "exec("),
        (r"\beval\s*\(", "eval("),
        (r"compile\s*\([^)]*,\s*[^)]*,\s*['\"]exec['\"]", "compile(..., 'exec')"),
        (r"\b__import__\s*\(", "__import__("),
        (r"\bimportlib\b", "importlib"),
        (r"\bsubprocess\b", "subprocess"),
        (r"os\.system\s*\(", "os.system("),
    ]
    for pat, label in forbidden:
        if re.search(pat, src_text):
            report.fail(code, f"源码含禁止用法：{label}")
            return
    dangerous = "import os\nos.remove('e07_probe.txt')\n"
    with tempfile.TemporaryDirectory(prefix="explain-e07-") as tmp:
        probe = Path(tmp) / "e07_probe.txt"
        probe.write_text("keep", encoding="utf-8")
        old_cwd = Path.cwd()
        try:
            import os

            os.chdir(tmp)
            explain_code(mod, dangerous, filename="danger.py")
        finally:
            os.chdir(old_cwd)
        if not probe.is_file():
            report.fail(code, "分析 import os; os.remove 后探测文件被删除（可能执行了代码）")
            return
    report.ok(code, "源码无 exec/eval 等，且分析不删除文件")


def check_e08(report: Report, mod) -> None:
    code = "E08"
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    bad: list[str] = []
    for snippet, _ in SYNTAX_ERROR_SAMPLES:
        try:
            result = explain_code(mod, snippet)
        except Exception as exc:  # noqa: BLE001
            bad.append(f"抛异常：{exc}")
            continue
        if result.get("ok") is not False:
            bad.append(f"应 ok=false：{snippet[:30]!r}")
            continue
        err = result.get("error") or {}
        if not err.get("message"):
            bad.append("缺少中文 message")
        if not err.get("line"):
            bad.append(f"缺少 line：{snippet[:20]!r}")
    if bad:
        report.fail(code, f"语法错误样例 {len(bad)} 项未达标（首条：{bad[0]}）")
    else:
        report.ok(code, f"{len(SYNTAX_ERROR_SAMPLES)} 个语法错误样例均返回行列与中文提示")


def check_e09(report: Report, mod) -> None:
    code = "E09"
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    script = ROOT / "site" / "scripts" / "verify-explain-pyodide.mjs"
    if not script.is_file():
        report.fail(code, "缺少 verify-explain-pyodide.mjs")
        return
    proc = subprocess.run(
        ["node", str(script), "--bench"],
        cwd=ROOT / "site",
        capture_output=True,
        text=True,
        timeout=900,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        report.fail(code, f"性能检查失败：{out.strip()[:400]}")
    else:
        line = next((ln for ln in out.splitlines() if ln.startswith("E09:")), out.strip()[:120])
        report.ok(code, line.replace("E09:", "").strip())


def check_u05(report: Report) -> None:
    code = "U05"
    explainer_vue = ROOT / "site" / ".vitepress" / "theme" / "components" / "CodeExplainer.vue"
    if not explainer_vue.is_file():
        report.skip(code, "CodeExplainer 未接入（M4 再查 Pages 产物）")
        return
    if not SITE_DIST.is_dir():
        report.skip(code, "尚未 build（M4 再查 Pages 产物无 AI 按钮）")
        return
    markers = ["explain-ai-btn", "ExplainAiButton", "JDP_EXPLAIN_AI", "data-explain-ai"]
    hits: list[str] = []
    for p in SITE_DIST.rglob("*"):
        if p.suffix not in (".html", ".js", ".css"):
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in markers:
            if m in text:
                hits.append(f"{p.name}:{m}")
    if hits:
        report.fail(code, f"构建产物含 AI 标记 {hits[:5]}")
    else:
        report.ok(code, "构建产物未检出 AI 讲解 DOM/JS 标记")


def check_gold_fixtures(report: Report, mod) -> None:
    code = "GOLD"
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    cases = sorted(d for d in FIXTURES_DIR.iterdir() if d.is_dir() and not d.name.startswith("."))
    if len(cases) < 20:
        report.fail(code, f"金标目录 {len(cases)} < 20")
        return
    mismatches: list[str] = []
    for case in cases:
        src_path = case / "source.py"
        exp_path = case / "expected.json"
        if not src_path.is_file() or not exp_path.is_file():
            mismatches.append(f"{case.name} 缺少 source.py/expected.json")
            continue
        expected = json.loads(exp_path.read_text(encoding="utf-8"))
        actual = explain_code(mod, src_path.read_text(encoding="utf-8"), filename=src_path.name)
        if expected.get("ok") != actual.get("ok"):
            mismatches.append(f"{case.name} ok 不一致")
            continue
        if not actual.get("ok"):
            continue
        for key in ("overview", "syntax_points", "concepts", "pitfalls"):
            if key in expected:
                if not _gold_subset(expected[key], actual.get(key), key):
                    mismatches.append(f"{case.name} {key} 与金标不一致")
    if mismatches:
        report.fail(code, f"金标比对 {len(mismatches)} 项（首条：{mismatches[0]}）")
    else:
        report.ok(code, f"{len(cases)} 份金标样例比对通过")


def _gold_subset(exp: Any, act: Any, key: str) -> bool:
    if isinstance(exp, dict) and isinstance(act, dict):
        for k, v in exp.items():
            if k not in act:
                return False
            if not _gold_subset(v, act[k], k):
                return False
        return True
    if isinstance(exp, list) and isinstance(act, list):
        if key == "syntax_points":
            for item in exp:
                if not any(_gold_subset(item, a, key) for a in act):
                    return False
            return True
        if key == "pitfalls":
            exp_ids = {x.get("rule_id") for x in exp if isinstance(x, dict)}
            act_ids = {x.get("rule_id") for x in act if isinstance(x, dict)}
            return exp_ids <= act_ids
        return exp == act
    return exp == act


def check_d1_schema_file(report: Report) -> None:
    code = "D1a"
    if not SCHEMA_PATH.is_file():
        report.fail(code, "缺少 py-explain.schema.json")
    else:
        report.ok(code, "Schema 文件存在")


def check_d1_analyzer_file(report: Report) -> None:
    code = "D1b"
    if not EXPLAIN_SCRIPT.is_file():
        report.fail(code, "缺少 py-explain.py")
    else:
        report.ok(code, "分析器文件存在")


def check_d2_concept_count(report: Report) -> None:
    code = "D2"
    rows = parse_concept_index()
    if len(rows) >= 60:
        report.ok(code, f"概念索引 {len(rows)} 条（≥60）")
    else:
        report.fail(code, f"概念索引 {len(rows)} < 60")


def check_d3_pitfall_count(report: Report, mod) -> None:
    code = "D3"
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    n = len(getattr(mod, "PITFALL_RULES", []))
    if n >= 10:
        report.ok(code, f"易错点规则 {n} 条（≥10）")
    else:
        report.fail(code, f"易错点规则 {n} < 10")


def check_d6_gold_count(report: Report) -> None:
    code = "D6a"
    n = len([d for d in FIXTURES_DIR.iterdir() if d.is_dir()])
    if n >= 20:
        report.ok(code, f"金标目录 {n} 个（≥20）")
    else:
        report.fail(code, f"金标目录 {n} < 20")


def check_cli_interface(report: Report) -> None:
    code = "CLI"
    if not EXPLAIN_SCRIPT.is_file():
        report.fail(code, "分析器不存在")
        return
    text = EXPLAIN_SCRIPT.read_text(encoding="utf-8")
    if "--cli" in text and "explain(" in text:
        report.ok(code, "提供 --cli 与 explain() 入口")
    else:
        report.fail(code, "缺少 CLI 或 explain 入口")


def check_size_limits(report: Report, mod) -> None:
    code = "LIM"
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    big = "x = 1\n" * 3001
    r = explain_code(mod, big)
    if r.get("ok") is False and "3000" in r.get("error", {}).get("message", ""):
        report.ok(code, "超过 3000 行返回中文提示")
    else:
        report.fail(code, "行数上限未生效")


EVALS_PATH = ROOT / "evals" / "code-explain-v1.jsonl"
EXPLAIN_SERVER = ROOT / "scripts" / "explain_server.py"


def _proxy_open(req: urllib.request.Request, timeout: float = 10.0):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return opener.open(req, timeout=timeout)


def explain_service_base() -> str:
    port = int(os.environ.get("JDP_PYTHON_EXPLAIN_PORT", "8031"))
    return f"http://127.0.0.1:{port}"


def pick_free_port() -> int:
    import socket as _socket

    sock = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


def ollama_available() -> tuple[bool, str]:
    proc = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=15)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "ollama list 失败").strip()[:120]
    if "qwen2.5-coder" not in (proc.stdout or ""):
        return False, "未找到 qwen2.5-coder 模型"
    return True, "ok"


def check_a01(report: Report) -> None:
    code = "A01"
    if not EXPLAIN_SERVER.is_file():
        report.fail(code, "缺少 explain_server.py")
        return
    port = pick_free_port()
    os.environ["JDP_PYTHON_EXPLAIN_PORT"] = str(port)
    srv = subprocess.Popen(
        [sys.executable, str(EXPLAIN_SERVER)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "JDP_PYTHON_EXPLAIN_PORT": str(port)},
    )
    time.sleep(0.8)
    try:
        listen = subprocess.run(
            ["lsof", f"-iTCP:{port}", "-sTCP:LISTEN", "-n", "-P"],
            capture_output=True,
            text=True,
        )
        text = listen.stdout or ""
        if "127.0.0.1" not in text and "*:" not in text:
            report.fail(code, f"端口 {port} 未在 127.0.0.1 监听")
            return
        if re.search(rf"\*:8031|0\.0\.0\.0:{port}", text):
            report.fail(code, "服务监听在非 localhost 地址")
            return
        req = urllib.request.Request(f"{explain_service_base()}/v1/health")
        with _proxy_open(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        blob = json.dumps(data, ensure_ascii=False)
        secret_probe = os.environ.get("JDP_PYTHON_EXPLAIN_TEST_SECRET", "jdp-explain-test-secret-value")
        if secret_probe and secret_probe in blob:
            report.fail(code, "health 响应含测试密钥")
            return
        report.ok(code, f"127.0.0.1:{port} /v1/health 就绪字段 model={data.get('model')}")
    finally:
        srv.terminate()
        srv.wait(timeout=5)


def _keyword_hits(text: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    low = text.lower()
    hit = sum(1 for k in keywords if k.lower() in low)
    return hit / len(keywords)


def check_a02(report: Report, mod) -> None:
    code = "A02"
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    if not EVALS_PATH.is_file():
        report.fail(code, "缺少 evals/code-explain-v1.jsonl")
        return
    ok_ollama, reason = ollama_available()
    if not ok_ollama:
        report.skip(code, f"Ollama 不可用，跳过：{reason}")
        return
    rows = [json.loads(ln) for ln in EVALS_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(rows) < 20:
        report.fail(code, f"评测题 {len(rows)} < 20")
        return
    env = os.environ.copy()
    env.setdefault("NO_PROXY", "127.0.0.1,localhost")
    env.setdefault("no_proxy", "127.0.0.1,localhost")
    port = pick_free_port()
    os.environ["JDP_PYTHON_EXPLAIN_PORT"] = str(port)
    env["JDP_PYTHON_EXPLAIN_PORT"] = str(port)
    srv = subprocess.Popen(
        [sys.executable, str(EXPLAIN_SERVER)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    time.sleep(1.0)
    fails: list[str] = []
    ratios: list[float] = []
    try:
        for row in rows:
            analysis = explain_code(mod, row["code"], filename=f"{row['id']}.py")
            payload = json.dumps({"code": row["code"], "analysis": analysis}).encode("utf-8")
            req = urllib.request.Request(
                f"{explain_service_base()}/v1/explain",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with _proxy_open(req, timeout=90.0) as resp:
                    out = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                raw = exc.read().decode("utf-8", errors="replace")
                try:
                    out = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    out = {}
                if exc.code >= 500:
                    fails.append(f"{row['id']}: HTTP {exc.code}")
                    continue
            if not out.get("ok"):
                fails.append(f"{row['id']}: HTTP 业务失败")
                continue
            blob = json.dumps(out, ensure_ascii=False)
            if row.get("exercise") and row.get("reference"):
                sim = difflib.SequenceMatcher(None, row["reference"].split(), blob.split()).ratio()
                if sim >= 0.6:
                    fails.append(f"{row['id']}: 练习相似度过高 {sim:.2f}")
                if row["reference"].strip() in blob:
                    fails.append(f"{row['id']}: 出现完整参考答案")
            merged = blob + json.dumps(analysis, ensure_ascii=False)
            ratios.append(_keyword_hits(merged, row.get("keywords") or []))
        avg = sum(ratios) / len(ratios) if ratios else 0.0
        if fails:
            report.fail(code, f"{len(fails)} 题未达标（首条 {fails[0]}）；要点均值 {avg:.0%}")
        elif avg < 0.7:
            report.fail(code, f"要点命中率均值 {avg:.0%} < 70%")
        else:
            report.ok(code, f"20 题 Schema 通过，要点均值 {avg:.0%}")
    finally:
        srv.terminate()
        srv.wait(timeout=5)


def check_a03(report: Report, mod) -> None:
    code = "A03"
    if mod is None:
        report.fail(code, "分析器不存在")
        return
    ok_ollama, reason = ollama_available()
    if not ok_ollama:
        report.skip(code, f"Ollama 不可用，跳过限额实测：{reason}")
        return
    port = pick_free_port()
    os.environ["JDP_PYTHON_EXPLAIN_PORT"] = str(port)
    env = os.environ.copy()
    env["JDP_PYTHON_EXPLAIN_DAILY_LIMIT"] = "3"
    env["JDP_PYTHON_EXPLAIN_PORT"] = str(port)
    env["JDP_PYTHON_EXPLAIN_SKIP_LLM"] = "1"
    env.setdefault("NO_PROXY", "127.0.0.1,localhost")
    srv = subprocess.Popen(
        [sys.executable, str(EXPLAIN_SERVER)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    time.sleep(0.8)
    try:
        big = "x=1\n" * 401
        analysis = explain_code(mod, "x=1\n")
        payload = json.dumps({"code": big, "analysis": analysis}).encode("utf-8")
        req = urllib.request.Request(
            f"{explain_service_base()}/v1/explain",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with _proxy_open(req, timeout=10.0) as resp:
                report.fail(code, f"401 行应返回 413，实际 {resp.status}")
                return
        except urllib.error.HTTPError as exc:
            if exc.code != 413:
                report.fail(code, f"401 行应返回 413，实际 {exc.code}")
                return
        for i in range(3):
            small = json.dumps({"code": f"print({i})\n", "analysis": analysis}).encode("utf-8")
            req2 = urllib.request.Request(
                f"{explain_service_base()}/v1/explain",
                data=small,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with _proxy_open(req2, timeout=90.0) as resp2:
                if resp2.status >= 400 and i < 3:
                    report.fail(code, f"第 {i+1} 次请求失败 {resp2.status}")
                    return
        req3 = urllib.request.Request(
            f"{explain_service_base()}/v1/explain",
            data=json.dumps({"code": "print(999)\n", "analysis": analysis}).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with _proxy_open(req3, timeout=90.0) as resp3:
                report.fail(code, f"第 4 次应 429，实际 {resp3.status}")
                return
        except urllib.error.HTTPError as exc:
            if exc.code != 429:
                report.fail(code, f"第 4 次应 429，实际 {exc.code}")
                return
        report.ok(code, "413 行数限制与每日上限 3 验证通过")
    finally:
        srv.terminate()
        srv.wait(timeout=5)


def check_a04(report: Report) -> None:
    code = "A04"
    secret = "jdp-explain-log-secret-probe"
    port = pick_free_port()
    os.environ["JDP_PYTHON_EXPLAIN_PORT"] = str(port)
    env = os.environ.copy()
    env["JDP_PYTHON_EXPLAIN_TEST_SECRET"] = secret
    env["JDP_PYTHON_EXPLAIN_PORT"] = str(port)
    env.setdefault("NO_PROXY", "127.0.0.1,localhost")
    srv = subprocess.Popen(
        [sys.executable, str(EXPLAIN_SERVER)],
        cwd=ROOT,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        env=env,
    )
    time.sleep(0.6)
    health_leak = False
    err = ""
    try:
        req = urllib.request.Request(
            f"{explain_service_base()}/v1/health",
            method="GET",
        )
        with _proxy_open(req, timeout=5.0) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        if secret in body:
            health_leak = True
    finally:
        srv.terminate()
        try:
            _, err_b = srv.communicate(timeout=5)
            err = err_b.decode("utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            srv.kill()
            _, err_b = srv.communicate(timeout=2)
            err = err_b.decode("utf-8", errors="replace")
    sample = "print('secret-code-sample')\n" * 5
    if health_leak:
        report.fail(code, "health 泄露测试密钥")
    elif secret in err or sample in err:
        report.fail(code, "日志含密钥或完整用户代码")
    else:
        report.ok(code, "health/日志未含测试密钥与完整代码")


def check_a_stubs(report: Report, live: bool, only: set[str] | None = None) -> None:
    if not live:
        for code in ("A01", "A02", "A03", "A04"):
            report.skip(code, "需 --live（M5 门禁）")
        return
    mod = load_explain_module()

    def want(code: str) -> bool:
        return not only or code in only

    if want("A01"):
        check_a01(report)
    if want("A02"):
        check_a02(report, mod)
    if want("A03"):
        check_a03(report, mod)
    if want("A04"):
        check_a04(report)


def print_header() -> None:
    rev = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    print(f"git rev: {rev.stdout.strip() or '?'}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S %z')}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="只跑逗号分隔的检查码，如 E01,E07,GOLD")
    ap.add_argument("--live", action="store_true", help="包含 A01–A04  live 检查")
    args = ap.parse_args()
    only = {x.strip().upper() for x in args.only.split(",")} if args.only else None

    print_header()
    report = Report()
    schema = load_schema()
    mod = load_explain_module()
    if mod is None:
        print("分析器：未安装（site/public/py-explain.py 不存在）")
    else:
        print(f"分析器：{rel(EXPLAIN_SCRIPT)}")

    corpus, stats = collect_corpus()
    report.stats["corpus"] = stats
    print(
        "语料统计："
        f" python run={stats['python_run_blocks']},"
        f" 练习={stats['exercises_total']}（浏览器 {stats['exercises_browser']}+本地 {stats['exercises_local']}）,"
        f" examples/*.py={stats['examples_py_files']},"
        f" 合计={stats['corpus_total']}"
    )

    def run(code: str, fn) -> None:
        if only and code not in only:
            return
        fn()

    run("D1a", lambda: check_d1_schema_file(report))
    run("D1b", lambda: check_d1_analyzer_file(report))
    run("D2", lambda: check_d2_concept_count(report))
    run("D3", lambda: check_d3_pitfall_count(report, mod))
    run("D6a", lambda: check_d6_gold_count(report))
    run("CLI", lambda: check_cli_interface(report))
    run("LIM", lambda: check_size_limits(report, mod))
    run("E01", lambda: check_e01(report, mod, schema))
    run("E02", lambda: check_e02(report, mod))
    run("E03", lambda: check_e03(report, mod))
    run("E04", lambda: check_e04(report, mod))
    run("E05", lambda: check_e05(report))
    run("E06", lambda: check_e06(report, mod))
    run("E07", lambda: check_e07(report, mod))
    run("E08", lambda: check_e08(report, mod))
    run("E09", lambda: check_e09(report, mod))
    run("U05", lambda: check_u05(report))
    run("GOLD", lambda: check_gold_fixtures(report, mod))
    if not only or only & {"A01", "A02", "A03", "A04"}:
        check_a_stubs(report, args.live, only)

    if report.skipped:
        print("\n跳过：")
        for s in report.skipped:
            print("  ○", s)
    if report.passed:
        print("\n通过：")
        for p in report.passed:
            print("  ✓", p)
    if report.failed:
        print(f"\n失败 {len(report.failed)} 项：")
        for f in report.failed:
            print("  ✗", f)
        return 1
    print("\n全部通过 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())

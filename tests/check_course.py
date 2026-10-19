"""课程质量校验器：执行 docs/课程 中的全部示例与练习，并检查结构、链接与版本标注。

用法（项目根目录）：
    uv run python tests/check_course.py               # 用项目解释器（.python-version = 3.12）
    python3 tests/check_course.py --python python3.14 # 指定其他解释器，可重复传入多个
    python3 tests/check_course.py -k 03-函数          # 只检查路径包含该片段的文件

代码块约定（与 site/.vitepress/lib/blocks.mjs 一致）：
    ```python run                    可运行示例，必须无异常结束
    ```python run raises=TypeError   预期抛出指定异常
    ```python exercise id=<ID>       练习：# --- starter --- / # --- solution --- / # --- check --- 三段
    ```python local exercise id=<ID> 仅本地执行的练习（浏览器不跑）
    ```python source=<相对路径>       与仓库文件逐字一致的完整源码副本
    ```python local                   仅本地 CPython 可运行（浏览器不执行）；校验器仍真实运行
    ```python fragment               片段，不做语法检查
    ```python                        静态代码，做语法检查（compile）

判定规则：
    run          → 正常结束；raises=X 时必须以异常 X 结束
    exercise     → solution + check 必须通过；starter + check 必须失败（证明检查有效）
执行方式：每个代码块在独立子进程中通过 site/public/py-runtime.py 运行（与浏览器端 Pyodide 共用同一运行时）。
"""

from __future__ import annotations

import argparse
import ast
import difflib
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
COURSE = DOCS / "课程"
RUNTIME = ROOT / "site" / "public" / "py-runtime.py"

LESSON_SECTIONS = ["目标", "核心概念", "易错点", "对照", "读代码", "练习", "小结", "延伸阅读"]
ALLOWED_DOMAINS = (
    "docs.python.org",
    "peps.python.org",
    "docs.astral.sh",
    "packaging.python.org",
    "docs.pytest.org",
    "mypy.readthedocs.io",
    "numpy.org",
    "pandas.pydata.org",
    "fastapi.tiangolo.com",
    "docs.pydantic.dev",
    "jupyter.org",
)
FENCE_RE = re.compile(r"^(`{3,})(.*)$")
SECTION_RE = re.compile(r"^# --- (starter|solution|check) ---\s*$")
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
VERSION_RE = re.compile(r"Python\s*3\.1[0-9]|3\.1[2-5]\+?\s*(?:起|新增|开始|版本)")


@dataclass
class Block:
    file: Path
    line: int
    lang: str
    flags: set[str]
    attrs: dict[str, str]
    content: str


@dataclass
class Report:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)

    def ok(self, kind: str, msg: str) -> None:
        self.counts[kind] = self.counts.get(kind, 0) + 1
        self.passed.append(msg)

    def fail(self, msg: str) -> None:
        self.failed.append(msg)


def parse_blocks(path: Path) -> list[Block]:
    blocks, lines = [], path.read_text(encoding="utf-8").split("\n")
    i = 0
    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        if not m:
            i += 1
            continue
        ticks, info = m.group(1), m.group(2).strip()
        start, body = i + 1, []
        i += 1
        while i < len(lines) and not (lines[i].startswith(ticks) and lines[i].strip() == ticks):
            body.append(lines[i])
            i += 1
        i += 1
        parts = info.split()
        lang = parts[0] if parts else ""
        flags = {p for p in parts[1:] if "=" not in p}
        attrs = dict(p.split("=", 1) for p in parts[1:] if "=" in p)
        blocks.append(Block(path, start, lang, flags, attrs, "\n".join(body) + "\n"))
    return blocks


def parse_exercise(content: str) -> dict[str, str]:
    out: dict[str, list[str]] = {"starter": [], "solution": [], "check": []}
    cur = None
    for line in content.split("\n"):
        m = SECTION_RE.match(line)
        if m:
            cur = m.group(1)
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip("\n") + "\n" for k, v in out.items()}


def run_code(python: str, code: str, check: str = "") -> dict:
    with tempfile.TemporaryDirectory(prefix="course-check-") as tmp:
        code_file, check_file = Path(tmp, "code.py"), Path(tmp, "check.py")
        code_file.write_text(code, encoding="utf-8")
        cmd = [python, str(RUNTIME), "--cli", str(code_file)]
        if check:
            check_file.write_text(check, encoding="utf-8")
            cmd.append(str(check_file))
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=tmp)
        except subprocess.TimeoutExpired:
            return {"ok": False, "err": "超时（60s）", "phase": "timeout", "errType": "Timeout"}
        try:
            return json.loads(proc.stdout.strip().splitlines()[-1])
        except (json.JSONDecodeError, IndexError):
            return {"ok": False, "err": f"运行时无结果：{proc.stderr[-2000:]}", "phase": "runtime", "errType": "?"}


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def check_blocks(blocks: list[Block], pythons: list[str], report: Report, seen_ids: dict[str, str]) -> None:
    jobs = []  # (描述, 期望, python, code, check, kind)
    for b in blocks:
        where = f"{rel(b.file)}:{b.line}"
        if b.lang != "python":
            continue
        if "exercise" in b.flags:
            ex_id = b.attrs.get("id")
            if not ex_id:
                report.fail(f"{where} 练习缺少 id=")
                continue
            if ex_id in seen_ids:
                report.fail(f"{where} 练习 id 重复：{ex_id}（首次出现于 {seen_ids[ex_id]}）")
            seen_ids[ex_id] = where
            ex = parse_exercise(b.content)
            missing = [k for k, v in ex.items() if not v.strip()]
            if missing:
                report.fail(f"{where} 练习 {ex_id} 缺少段落：{missing}")
                continue
            sol_kind = "local_exercise" if "local" in b.flags else "exercise"
            for py in pythons:
                jobs.append((f"{where} [{ex_id}] solution", ("ok", None), py, ex["solution"], ex["check"], sol_kind))
                jobs.append((f"{where} [{ex_id}] starter", ("fail", None), py, ex["starter"], ex["check"], "starter"))
        elif "run" in b.flags or "local" in b.flags:
            for py in pythons:
                jobs.append((where, ("raises", b.attrs["raises"]) if "raises" in b.attrs else ("ok", None), py, b.content, "", "example"))
        elif "source" in b.attrs:
            target = ROOT / b.attrs["source"]
            if not target.exists():
                report.fail(f"{where} source 文件不存在：{b.attrs['source']}")
            elif target.read_text(encoding="utf-8") != b.content:
                report.fail(f"{where} 与 {b.attrs['source']} 内容不一致（请同步副本）")
            else:
                report.ok("source", f"{where} 与 {b.attrs['source']} 一致")
        elif "fragment" not in b.flags:
            try:
                compile(b.content, where, "exec")
                report.ok("static", where)
            except SyntaxError as e:
                report.fail(f"{where} 静态代码语法错误：{e}")

    def work(job):
        where, (expect, arg), py, code, check, kind = job
        return job, run_code(py, code, check)

    with ThreadPoolExecutor(max_workers=8) as pool:
        for job, res in pool.map(work, jobs):
            where, (expect, arg), py, _, _, kind = job
            tag = f"{where} ({Path(py).name})"
            if expect == "ok" and res["ok"]:
                report.ok(kind, tag)
            elif expect == "raises" and not res["ok"] and res.get("errType") == arg and res.get("phase") == "code":
                report.ok(kind, tag)
            elif expect == "fail" and not res["ok"]:
                report.ok(kind, tag)
            elif expect == "fail":
                report.fail(f"{tag} starter 竟然通过了检查（检查太弱或 starter 已是答案）")
            else:
                want = f"预期抛出 {arg}" if expect == "raises" else "预期成功"
                report.fail(f"{tag} {want}，实际：{res.get('errType') or '成功'}\n    {res.get('err', '').strip()[-800:]}")


V21_MIN_BODY_LINES = 150
V21_MIN_RUN_BLOCKS = 3
V21_MIN_EXERCISE_BLOCKS = 2
V21_MIN_COMPARE_ROWS = 3
V21_STAGE_MIN = 12
V21_FORBIDDEN_PLACEHOLDERS = ("见官方文档", "TODO", "待补充", "后续补充")
V21_DUP_LINE_MAX = 3  # 同一归一化正文行/句在 12–24 阶段课程中出现超过此次数视为凑数
V22_DUP_IN_LESSON_MAX = 2  # 同一课内归一化行/句超过此次数视为凑数
V22_FILLER_MARKERS = (
    ("课堂延展", "D1 课堂延展小节"),
    ("达标备注", "D2 达标备注行"),
    ("三分钟讲清", "D3 模板自测题"),
    ("写下路径与行号范围", "D3 模板自测题"),
    ("可与 tests/check_course.py 一并验收", "写给检查脚本的句子"),
    ("本课正文非空行已对齐", "写给检查脚本的句子"),
)
PYODIDE_FORBIDDEN_IN_RUN = re.compile(
    r"\b(threading|multiprocessing|subprocess|socket)\b|"
    r"ThreadPoolExecutor|ProcessPoolExecutor|\bas_completed\b",
    re.I,
)
_CF_IMPORT_RE = re.compile(r"from\s+concurrent\.futures\s+import\s+([^\n#]+)", re.I)
_CF_IMPORT_ALLOWED = frozenset({"Future", "CancelledError", "TimeoutError"})
V23_MIN_RUN_EFFECTIVE = 5
V23_MIN_RAISES_EFFECTIVE = 3
V23_RUN_SIMILARITY_MAX = 0.85
_IMPORT_PRINT_LINE_RE = re.compile(
    r"^(?:import\s+\S+|from\s+\S+\s+import\s+.+|print\s*\(.*\))\s*$"
)
_V23_TAUTOLOGY_RE = re.compile(
    r"\bor\s+True\b|assert\s+True\b",
    re.I,
)

V231_MIN_REGRESSION_EFFECTIVE = 8

# v2.3.1 回归：课文件（相对仓库根）与第几个 python run 块（从 1 起）
V231_RUN_BLOCK_SPECS: list[tuple[str, int]] = [
    ("docs/课程/14-文本文件与命令行/01-编码与bytes.md", 4),
    ("docs/课程/14-文本文件与命令行/01-编码与bytes.md", 5),
    ("docs/课程/14-文本文件与命令行/01-编码与bytes.md", 8),
    ("docs/课程/14-文本文件与命令行/01-编码与bytes.md", 9),
    ("docs/课程/14-文本文件与命令行/02-re正则.md", 1),
    ("docs/课程/17-打包与发布/01-wheel与构建后端.md", 4),
    ("docs/课程/14-文本文件与命令行/01-编码与bytes.md", 2),
    ("docs/课程/14-文本文件与命令行/01-编码与bytes.md", 7),
    ("docs/课程/18-并发/03-free-threaded现状.md", 1),
    ("docs/课程/19-asyncio/02-gather与TaskGroup.md", 1),
    ("docs/课程/19-asyncio/02-gather与TaskGroup.md", 2),
    ("docs/课程/17-打包与发布/03-发布流程.md", 2),
    ("docs/课程/17-打包与发布/03-发布流程.md", 4),
]


def _function_param_names(args: ast.arguments) -> set[str]:
    names: set[str] = set()
    for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs):
        names.add(arg.arg)
    if args.vararg:
        names.add(args.vararg.arg)
    if args.kwarg:
        names.add(args.kwarg.arg)
    return names


def _unused_assigned_in_body(body: list[ast.stmt], param_names: set[str]) -> list[tuple[str, int]]:
    assigned: dict[str, int] = {}
    loaded: set[str] = set()
    nested: list[tuple[str, int]] = []

    class Walker(ast.NodeVisitor):
        def visit_Name(self, node: ast.Name) -> None:
            if isinstance(node.ctx, ast.Store):
                if not node.id.startswith("_") and node.id not in param_names:
                    assigned[node.id] = node.lineno
            elif isinstance(node.ctx, ast.Load):
                loaded.add(node.id)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            nested.extend(_unused_assigned_in_body(node.body, _function_param_names(node.args)))

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            nested.extend(_unused_assigned_in_body(node.body, _function_param_names(node.args)))

    Walker().visit(ast.Module(body=body, type_ignores=[]))
    outer = [(name, lineno) for name, lineno in assigned.items() if name not in loaded]
    return outer + nested


def unused_assigned_variables(content: str) -> list[tuple[str, int]]:
    """赋值后从未读取的变量（_ 前缀与函数形参除外）。语法错误时返回空列表。"""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []
    return _unused_assigned_in_body(tree.body, set())


def nth_python_run_block(path: Path, index: int) -> Block:
    """课内第 index 个 python run 块（从 1 起）。"""
    runs = [b for b in parse_blocks(path) if b.lang == "python" and "run" in b.flags]
    if index < 1 or index > len(runs):
        raise IndexError(f"{rel(path)} 仅有 {len(runs)} 个 run 块，请求第 {index} 个")
    return runs[index - 1]


def check_v231_r6_unused_assignments(blocks: list[Block], report: Report) -> None:
    """v2.3.1 R6：目标 13 个 python run 块不得有赋值后未读的变量。"""
    failures: list[str] = []
    for rel_path, index in V231_RUN_BLOCK_SPECS:
        try:
            b = nth_python_run_block(ROOT / rel_path, index)
        except IndexError as e:
            failures.append(f"v2.3.1 R6 {rel_path} run#{index}: {e}")
            continue
        where = f"{rel(b.file)}:{b.line}"
        for name, lineno in unused_assigned_variables(b.content):
            failures.append(f"v2.3.1 R6 {where} 变量 {name!r} 赋值后未读（约第 {lineno} 行）")
    if failures:
        for msg in failures:
            report.fail(msg)
    else:
        report.ok("v231_r6", "v2.3.1 R6 未使用赋值")


V232_R7_MIN_PRINTS = 3
V232_R7_LITERAL_PRINT_RATIO = 0.5


def _fstring_is_literal(node: ast.JoinedStr) -> bool:
    return all(isinstance(part, ast.Constant) and isinstance(part.value, str) for part in node.values)


def _is_sys_version_attr(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "sys"
        and node.attr in ("version", "version_info")
    )


def _is_env_probe_call(node: ast.Call) -> bool:
    if isinstance(node.func, ast.Name) and node.func.id == "hasattr":
        return True
    if _is_sys_version_attr(node.func):
        return True
    return False


class _LiteralSourceAnalyzer:
    """判断表达式是否仅来自块内字面量（v2.3.2 R7）。语法错误时保守为「非字面量」。"""

    def __init__(self, tree: ast.Module) -> None:
        self._tree = tree
        self._literal_funcs: set[str] = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self._function_returns_only_literals(node):
                    self._literal_funcs.add(node.name)

    def _function_returns_only_literals(self, fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        env: dict[str, bool] = {a.arg: False for a in fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs}
        if fn.args.vararg:
            env[fn.args.vararg.arg] = False
        if fn.args.kwarg:
            env[fn.args.kwarg.arg] = False
        return self._body_preserves_literals(fn.body, env)

    def _body_preserves_literals(self, body: list[ast.stmt], env: dict[str, bool]) -> bool:
        for stmt in body:
            if isinstance(stmt, ast.Return):
                if stmt.value is None:
                    return False
                if not self._expr_literal(stmt.value, env):
                    return False
            elif isinstance(stmt, ast.Assign):
                val_lit = self._expr_literal(stmt.value, env)
                for t in stmt.targets:
                    self._assign_target(t, val_lit, env)
            elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                val_lit = self._expr_literal(stmt.value, env)
                self._assign_target(stmt.target, val_lit, env)
            elif isinstance(stmt, ast.AugAssign):
                if not isinstance(stmt.target, ast.Name):
                    return False
                env[stmt.target.id] = False
            elif isinstance(stmt, ast.If):
                if not self._body_preserves_literals(stmt.body, env.copy()):
                    return False
                if not self._body_preserves_literals(stmt.orelse, env.copy()):
                    return False
            elif isinstance(stmt, ast.For):
                iter_lit = self._expr_literal(stmt.iter, env)
                loop_env = env.copy()
                self._bind_loop_target(stmt.target, iter_lit, loop_env)
                if not self._body_preserves_literals(stmt.body, loop_env):
                    return False
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                self._maybe_literal_append(stmt.value, env)
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Try, ast.With)):
                return False
        return True

    def _name_from_target(self, target: ast.AST) -> str:
        if isinstance(target, ast.Name):
            return target.id
        raise ValueError("complex target")

    def _assign_target(self, target: ast.AST, literal: bool, env: dict[str, bool]) -> None:
        if isinstance(target, ast.Name):
            env[target.id] = literal
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._assign_target(elt, literal, env)

    def _bind_loop_target(self, target: ast.AST, iter_literal: bool, env: dict[str, bool]) -> None:
        if not iter_literal:
            return
        if isinstance(target, ast.Name):
            env[target.id] = True
        elif isinstance(target, ast.Tuple):
            for elt in target.elts:
                self._bind_loop_target(elt, True, env)

    def _maybe_literal_append(self, call: ast.Call, env: dict[str, bool]) -> None:
        if not isinstance(call.func, ast.Attribute) or call.func.attr != "append":
            return
        if not isinstance(call.func.value, ast.Name):
            return
        name = call.func.value.id
        if not env.get(name):
            return
        if len(call.args) != 1 or call.keywords:
            env[name] = False
            return
        if not self._expr_literal(call.args[0], env):
            env[name] = False

    def _expr_literal(self, node: ast.AST | None, env: dict[str, bool]) -> bool:
        if node is None:
            return False
        if isinstance(node, ast.Constant):
            return True
        if isinstance(node, ast.JoinedStr):
            return _fstring_is_literal(node)
        if isinstance(node, ast.Name):
            return env.get(node.id, False)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return self._expr_literal(node.operand, env)
        if isinstance(node, ast.IfExp):
            return self._expr_literal(node.body, env) and self._expr_literal(node.orelse, env)
        if isinstance(node, ast.List):
            return all(self._expr_literal(e, env) for e in node.elts)
        if isinstance(node, ast.Tuple):
            return all(self._expr_literal(e, env) for e in node.elts)
        if isinstance(node, ast.Set):
            return all(self._expr_literal(e, env) for e in node.elts)
        if isinstance(node, ast.Dict):
            return all(
                (k is None or self._expr_literal(k, env)) and self._expr_literal(v, env)
                for k, v in zip(node.keys, node.values)
            )
        if isinstance(node, ast.Subscript):
            return self._expr_literal(node.value, env) and self._expr_literal(node.slice, env)
        if isinstance(node, ast.Attribute):
            base_lit = self._expr_literal(node.value, env)
            if base_lit and node.attr in ("items", "keys", "values"):
                return True
            return False
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            return self._comp_literal(node, env)
        if isinstance(node, ast.DictComp):
            return self._dict_comp_literal(node, env)
        if isinstance(node, ast.Call):
            if _is_env_probe_call(node):
                return True
            if isinstance(node.func, ast.Name) and node.func.id in self._literal_funcs:
                return all(self._expr_literal(a, env) for a in node.args) and all(
                    self._expr_literal(kw.value, env) for kw in node.keywords
                )
            return False
        return False

    def _comp_literal(self, node: ast.ListComp | ast.SetComp | ast.GeneratorExp, env: dict[str, bool]) -> bool:
        loop_env = env.copy()
        for gen in node.generators:
            if not self._expr_literal(gen.iter, loop_env):
                return False
            self._bind_comp_targets(gen.target, loop_env)
            for if_clause in gen.ifs:
                # 过滤条件允许任意表达式，不改变「元素为字面量」的判定
                pass
        return self._expr_literal(node.elt, loop_env)

    def _dict_comp_literal(self, node: ast.DictComp, env: dict[str, bool]) -> bool:
        loop_env = env.copy()
        for gen in node.generators:
            if not self._expr_literal(gen.iter, loop_env):
                return False
            self._bind_comp_targets(gen.target, loop_env)
        return self._expr_literal(node.key, loop_env) and self._expr_literal(node.value, loop_env)

    def _bind_comp_targets(self, target: ast.AST, env: dict[str, bool]) -> None:
        if isinstance(target, ast.Name):
            env[target.id] = True
        elif isinstance(target, ast.Tuple):
            for elt in target.elts:
                self._bind_comp_targets(elt, env)

    def _print_is_prewritten(self, node: ast.Call, env: dict[str, bool]) -> bool:
        args = list(node.args)
        for kw in node.keywords:
            if kw.arg is None:
                return False
            args.append(kw.value)
        if not args:
            return True
        return all(self._expr_literal(a, env) for a in args)

    def count_prewritten_prints(self) -> tuple[int, int]:
        """返回 (print 调用数, 预写文字 print 数)。"""
        self._counters = [0, 0]
        env: dict[str, bool] = {}
        self._walk_stmts(self._tree.body, env)
        return self._counters[0], self._counters[1]

    def _walk_stmts(self, body: list[ast.stmt], env: dict[str, bool]) -> None:
        for stmt in body:
            self._walk_stmt(stmt, env)

    def _walk_stmt(self, stmt: ast.stmt, env: dict[str, bool]) -> None:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if isinstance(call.func, ast.Name) and call.func.id == "print":
                self._counters[0] += 1
                if self._print_is_prewritten(call, env):
                    self._counters[1] += 1
            else:
                self._maybe_literal_append(call, env)
        elif isinstance(stmt, ast.Assign):
            val_lit = self._expr_literal(stmt.value, env)
            for t in stmt.targets:
                self._assign_target(t, val_lit, env)
        elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
            val_lit = self._expr_literal(stmt.value, env)
            self._assign_target(stmt.target, val_lit, env)
        elif isinstance(stmt, ast.AugAssign):
            if isinstance(stmt.target, ast.Name):
                env[stmt.target.id] = False
        elif isinstance(stmt, ast.For):
            iter_lit = self._expr_literal(stmt.iter, env)
            loop_env = env.copy()
            self._bind_loop_target(stmt.target, iter_lit, loop_env)
            self._walk_stmts(stmt.body, loop_env)
        elif isinstance(stmt, ast.If):
            then_env = env.copy()
            self._walk_stmts(stmt.body, then_env)
            else_env = env.copy()
            self._walk_stmts(stmt.orelse, else_env)
        elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            pass
        elif isinstance(stmt, ast.With):
            self._walk_stmts(stmt.body, env)


def prewritten_print_counts(content: str) -> tuple[int, int]:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return 0, 0
    return _LiteralSourceAnalyzer(tree).count_prewritten_prints()


def run_block_fails_v232_r7(content: str) -> bool:
    total, literal = prewritten_print_counts(content)
    if total < V232_R7_MIN_PRINTS:
        return False
    return literal / total >= V232_R7_LITERAL_PRINT_RATIO


def check_v232_r7_prewritten_prints(blocks: list[Block], report: Report) -> None:
    """v2.3.2 R7：阶段 12–24 的 python run 块不得主要在打印预写文字。"""
    failures: list[str] = []
    for b in blocks:
        stage = _lesson_stage(b.file)
        if stage is None or stage < V21_STAGE_MIN:
            continue
        if b.lang != "python" or "run" not in b.flags:
            continue
        total, literal = prewritten_print_counts(b.content)
        if total < V232_R7_MIN_PRINTS:
            continue
        if literal / total >= V232_R7_LITERAL_PRINT_RATIO:
            where = f"{rel(b.file)}:{b.line}"
            failures.append(
                f"v2.3.2 R7 {where} print {total} 个中有 {literal} 个为预写文字 "
                f"({literal / total:.0%} >= {V232_R7_LITERAL_PRINT_RATIO:.0%})"
            )
    if failures:
        for msg in failures:
            report.fail(msg)
    else:
        report.ok("v232_r7", "v2.3.2 R7 预写文字打印")


def _lesson_stage(path: Path) -> int | None:
    if path.parent.parent != COURSE:
        return None
    m = re.match(r"^(\d\d)-", path.parent.name)
    if not m or not re.match(r"^\d\d-", path.name):
        return None
    return int(m.group(1))


def _body_without_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :]
    return text


def _count_compare_rows(text: str) -> int:
    """对照表中的数据行（非表头、非 --- 分隔行）。"""
    if "## 对照" not in text:
        return 0
    section = text.split("## 对照", 1)[1].split("\n## ", 1)[0]
    rows = 0
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        inner = line.strip("|").strip()
        if not inner or re.match(r"^[-:\s|]+$", inner):
            continue
        if "概念" in inner and "Python" in inner:
            continue
        rows += 1
    return rows


def _collect_v21_lines(path: Path) -> list[str]:
    body = _body_without_frontmatter(path.read_text(encoding="utf-8"))
    lines = []
    in_fence = False
    for line in body.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("|"):
            continue
        lines.append(s)
    return lines


def check_v21_lesson(path: Path, report: Report) -> None:
    stage = _lesson_stage(path)
    if stage is None or stage < V21_STAGE_MIN:
        return
    text = path.read_text(encoding="utf-8")
    where = rel(path)
    body = _body_without_frontmatter(text)
    n_body = len([ln for ln in body.splitlines() if ln.strip()])
    if n_body < V21_MIN_BODY_LINES:
        report.fail(f"{where} v2.1 正文行数 {n_body} < {V21_MIN_BODY_LINES}")
    n_run = len(re.findall(r"^```python run(?:\s|$)", text, re.M))
    if n_run < V21_MIN_RUN_BLOCKS:
        report.fail(f"{where} v2.1 可运行示例 {n_run} < {V21_MIN_RUN_BLOCKS}")
    n_ex = len(re.findall(r"^```python exercise", text, re.M))
    if n_ex < V21_MIN_EXERCISE_BLOCKS:
        report.fail(f"{where} v2.1 练习 {n_ex} < {V21_MIN_EXERCISE_BLOCKS}")
    for ph in V21_FORBIDDEN_PLACEHOLDERS:
        if ph in text:
            report.fail(f"{where} v2.1 含占位：{ph}")
    if "略" in text and "策略" not in text and "省略" not in text:
        report.fail(f"{where} v2.1 含占位：略")
    n_cmp = _count_compare_rows(text)
    if n_cmp < V21_MIN_COMPARE_ROWS:
        report.fail(f"{where} v2.1 对照表数据行 {n_cmp} < {V21_MIN_COMPARE_ROWS}")
    else:
        report.ok("v21_structure", f"{where} v2.1 结构量化")


def normalize_v22_text(line: str) -> str:
    """归一化正文行/句：抹平课名、课号、路径与数字，用于 v2.2 凑数查重。"""
    s = line.strip()
    if not s:
        return ""
    s = re.sub(r"「[^」]*」", "「§TITLE」", s)
    s = re.sub(r"\b\d{1,2}\.\d{1,2}\b", "§N", s)
    s = re.sub(r"·\d+", "·§N", s)
    s = re.sub(r"docs/[^\s）」]*", "docs/§PATH", s)
    s = re.sub(r"examples/[^\s）」]*", "examples/§PATH", s)
    s = re.sub(r"[^\s）」]+\.(?:md|py)\b", "§FILE", s)
    s = re.sub(r"\d+", "§N", s)
    return s.strip()


def _split_v22_sentences(line: str) -> list[str]:
    parts = re.split(r"(?<=[。！？])", line)
    return [p.strip() for p in parts if p.strip()]


def _normalize_code_block(content: str) -> str:
    out: list[str] = []
    for raw in content.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return "".join(out)


def _effective_code_lines(content: str) -> list[str]:
    """非空、去掉行尾注释后的代码行（用于 v2.3 R1/R3）。"""
    lines: list[str] = []
    for raw in content.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            lines.append(line)
    return lines


def _run_block_import_print_only(content: str) -> bool:
    """有效代码行是否全部为 import/from-import 或 print(...)（v2.3 R2）。"""
    eff = _effective_code_lines(content)
    if not eff:
        return False
    return all(_IMPORT_PRINT_LINE_RE.match(ln) for ln in eff)


def check_v23_weak_run_blocks(blocks: list[Block], report: Report) -> None:
    """v2.3：阶段 12–24 的 python run 块质量门禁 R1–R5。"""
    run_blocks: list[Block] = []
    failures: list[str] = []
    for b in blocks:
        stage = _lesson_stage(b.file)
        if stage is None or stage < V21_STAGE_MIN:
            continue
        if b.lang != "python" or "run" not in b.flags:
            continue
        run_blocks.append(b)
        where = f"{rel(b.file)}:{b.line}"
        n_eff = len(_effective_code_lines(b.content))
        if "raises" not in b.attrs:
            if n_eff < V23_MIN_RUN_EFFECTIVE:
                failures.append(f"v2.3 R1 {where} 有效代码 {n_eff} 行 < {V23_MIN_RUN_EFFECTIVE}")
            if _run_block_import_print_only(b.content):
                failures.append(f"v2.3 R2 {where} 仅 import/print")
        else:
            if n_eff < V23_MIN_RAISES_EFFECTIVE:
                failures.append(f"v2.3 R3 {where} raises 演示有效代码 {n_eff} 行 < {V23_MIN_RAISES_EFFECTIVE}")
        if _V23_TAUTOLOGY_RE.search(b.content):
            failures.append(f"v2.3 R5 {where} 含恒真断言（or True / assert True）")

    norms: list[tuple[str, str, int]] = []
    for b in run_blocks:
        norm = _normalize_code_block(b.content)
        if norm:
            norms.append((norm, rel(b.file), b.line))
    for i in range(len(norms)):
        for j in range(i + 1, len(norms)):
            a, b = norms[i][0], norms[j][0]
            if len(a) < 8 and len(b) < 8:
                continue
            ratio = difflib.SequenceMatcher(None, a, b).ratio()
            if ratio >= V23_RUN_SIMILARITY_MAX:
                failures.append(
                    f"v2.3 R4 {norms[i][1]}:{norms[i][2]} 与 {norms[j][1]}:{norms[j][2]} "
                    f"相似度 {ratio:.3f} >= {V23_RUN_SIMILARITY_MAX}"
                )

    if failures:
        for msg in failures:
            report.fail(msg)
    else:
        report.ok("v23_run_quality", "v2.3 弱示例门禁 R1–R5")


def _code_for_forbidden_scan(content: str) -> str:
    return "\n".join(raw.split("#", 1)[0] for raw in content.splitlines())


def pyodide_forbidden_in_block(content: str) -> bool:
    """浏览器 run/exercise 禁止线程/进程/网络 API；concurrent.futures 仅放行 Future 等句柄类型。"""
    scan = _code_for_forbidden_scan(content)
    if PYODIDE_FORBIDDEN_IN_RUN.search(scan):
        return True
    if re.search(r"\bimport\s+concurrent\.futures\b", scan):
        return True
    for m in _CF_IMPORT_RE.finditer(scan):
        names = re.sub(r"\([^)]*\)", "", m.group(1))
        for part in names.split(","):
            name = part.strip().split(" as ", 1)[0].strip()
            if name and name not in _CF_IMPORT_ALLOWED:
                return True
    return False


def check_v22_filler_markers(course_files: list[Path], report: Report) -> None:
    v21 = [p for p in course_files if (_lesson_stage(p) or 0) >= V21_STAGE_MIN]
    hits: list[str] = []
    for marker, label in V22_FILLER_MARKERS:
        n = sum(marker in p.read_text(encoding="utf-8") for p in v21)
        if n:
            hits.append(f"{label}（{marker!r}）出现 {n} 处")
    if hits:
        report.fail("v2.2 凑数标记未清零：" + "；".join(hits))
    else:
        report.ok("v22_filler", "v2.2 凑数标记清零")


def check_v22_duplicate_text(course_files: list[Path], report: Report) -> None:
    v21 = [p for p in course_files if (_lesson_stage(p) or 0) >= V21_STAGE_MIN]
    cross_line: dict[str, set[Path]] = {}
    cross_sent: dict[str, set[Path]] = {}
    in_lesson_line: list[tuple[Path, str, int]] = []
    in_lesson_sent: list[tuple[Path, str, int]] = []

    for p in v21:
        line_counts: dict[str, int] = {}
        sent_counts: dict[str, int] = {}
        for raw in _collect_v21_lines(p):
            norm = normalize_v22_text(raw)
            if len(norm) < 12:
                continue
            line_counts[norm] = line_counts.get(norm, 0) + 1
            cross_line.setdefault(norm, set()).add(p)
            for sent in _split_v22_sentences(raw):
                ns = normalize_v22_text(sent)
                if len(ns) < 12:
                    continue
                sent_counts[ns] = sent_counts.get(ns, 0) + 1
                cross_sent.setdefault(ns, set()).add(p)
        for norm, c in line_counts.items():
            if c > V22_DUP_IN_LESSON_MAX:
                in_lesson_line.append((p, norm, c))
        for norm, c in sent_counts.items():
            if c > V22_DUP_IN_LESSON_MAX:
                in_lesson_sent.append((p, norm, c))

    cross_off = [(n, len(ps)) for n, ps in cross_line.items() if len(ps) > V21_DUP_LINE_MAX]
    sent_off = [(n, len(ps)) for n, ps in cross_sent.items() if len(ps) > V21_DUP_LINE_MAX]
    failures: list[str] = []
    if cross_off:
        cross_off.sort(key=lambda x: -x[1])
        sample = "; ".join(f"×{n}课" for _, n in cross_off[:3])
        failures.append(f"跨课重复归一化行 {len(cross_off)} 条（>{V21_DUP_LINE_MAX} 课），{sample}")
    if sent_off:
        sent_off.sort(key=lambda x: -x[1])
        failures.append(f"跨课重复归一化句 {len(sent_off)} 条（>{V21_DUP_LINE_MAX} 课）")
    if in_lesson_line:
        failures.append(f"课内重复归一化行 {len(in_lesson_line)} 处（>{V22_DUP_IN_LESSON_MAX} 次/课）")
    if in_lesson_sent:
        failures.append(f"课内重复归一化句 {len(in_lesson_sent)} 处（>{V22_DUP_IN_LESSON_MAX} 次/课）")
    if failures:
        report.fail("v2.2 正文查重：" + "；".join(failures))
    else:
        report.ok("v22_dup", "v2.2 正文查重")


def check_v22_duplicate_code_blocks(blocks: list[Block], report: Report) -> None:
    indexed: list[tuple[str, Path, int]] = []
    for b in blocks:
        stage = _lesson_stage(b.file)
        if stage is None or stage < V21_STAGE_MIN:
            continue
        if b.lang != "python":
            continue
        if "run" not in b.flags and "exercise" not in b.flags and "local" not in b.flags:
            continue
        norm = _normalize_code_block(b.content)
        if len(norm) < 24:
            continue
        indexed.append((norm, b.file, b.line))
    by_hash: dict[str, list[tuple[Path, int]]] = {}
    for norm, path, line in indexed:
        by_hash.setdefault(norm, []).append((path, line))
    dup_groups = [loc for loc in by_hash.values() if len({p for p, _ in loc}) >= 2]
    if dup_groups:
        sample = dup_groups[0]
        a, b = sample[0], sample[1] if len(sample) > 1 else sample[0]
        report.fail(
            f"v2.2 代码块查重：{len(dup_groups)} 组完全相同（去空白注释后），"
            f"例 {rel(a[0])}:{a[1]} 与 {rel(b[0])}:{b[1]}"
        )
    else:
        report.ok("v22_code_dup", "v2.2 代码块查重")


def check_v22_pyodide_forbidden(blocks: list[Block], report: Report) -> None:
    bad: list[str] = []
    for b in blocks:
        stage = _lesson_stage(b.file)
        if stage is None or stage < V21_STAGE_MIN:
            continue
        if b.lang != "python":
            continue
        if "local" in b.flags:
            continue
        if "run" not in b.flags and "exercise" not in b.flags:
            continue
        if not pyodide_forbidden_in_block(b.content):
            continue
        bad.append(f"{rel(b.file)}:{b.line}")
    if bad:
        report.fail(f"v2.2 浏览器不可运行块（run/exercise 含线程/进程/网络 API）{len(bad)} 个：{', '.join(bad[:8])}")
    else:
        report.ok("v22_pyodide", "v2.2 浏览器可运行块")


def check_v21_duplicate_lines(course_files: list[Path], report: Report) -> None:
    """保留 v2.1 原文整行查重（阈值 3 课），与 v2.2 归一化查重并存。"""
    v21 = [p for p in course_files if (_lesson_stage(p) or 0) >= V21_STAGE_MIN]
    counts: dict[str, int] = {}
    for p in v21:
        seen_in_file: set[str] = set()
        for line in _collect_v21_lines(p):
            if line in seen_in_file:
                continue
            seen_in_file.add(line)
            counts[line] = counts.get(line, 0) + 1
    offenders = [(line, n) for line, n in counts.items() if n > V21_DUP_LINE_MAX]
    if offenders:
        offenders.sort(key=lambda x: -x[1])
        sample = "; ".join(f"「{t[:40]}…」×{n}" if len(t) > 40 else f"「{t}」×{n}" for t, n in offenders[:5])
        report.fail(f"v2.1 重复正文行 {len(offenders)} 条（>3 课重复），示例：{sample}")
    else:
        report.ok("v21_dup", "v2.1 重复行检查")


def check_structure(path: Path, report: Report) -> None:
    text = path.read_text(encoding="utf-8")
    where = rel(path)
    is_lesson = path.parent.parent == COURSE and re.match(r"^\d\d-", path.name) and re.match(r"^\d\d-", path.parent.name)
    if is_lesson:
        if not re.match(r"^---\n[\s\S]*?\btitle:", text):
            report.fail(f"{where} 缺少 frontmatter title")
        heads = re.findall(r"^## (.+)$", text, re.M)
        missing = [s for s in LESSON_SECTIONS if not any(h.strip().startswith(s) for h in heads)]
        if missing:
            report.fail(f"{where} 缺少章节：{missing}")
        if "```python run" not in text:
            report.fail(f"{where} 没有可运行示例")
        if not re.search(r"^```python (?:local )?exercise", text, re.M):
            report.fail(f"{where} 没有练习")
        if not missing:
            report.ok("structure", where)
    if VERSION_RE.search(text) and "核对日期" not in text:
        report.fail(f"{where} 提到了具体 Python 版本，但缺少“核对日期”标注")


def allowed_course_link(path: Path, href: str) -> bool:
    """官方参考来源；仅术语表可复用指定 Wiki 的通用定义。"""
    url = urlsplit(href)
    if url.netloc in ALLOWED_DOMAINS:
        return True
    return (
        path.resolve() == (COURSE / "附录" / "术语表.md").resolve()
        and url.scheme == "https"
        and url.netloc == "github.com"
        and not url.query
        and re.fullmatch(
            r"/lixudong1649/jdp-wiki/blob/main/content/terms/[a-z0-9]+(?:-[a-z0-9]+)*\.md",
            url.path,
        ) is not None
    )


def check_links(path: Path, report: Report, strict_domains: bool) -> None:
    text = path.read_text(encoding="utf-8")
    # 去掉代码块，避免把代码中的方括号当作链接
    text = re.sub(r"^(`{3,}).*?^\1\s*$", "", text, flags=re.M | re.S)
    text = re.sub(r"`[^`\n]+`", "", text)  # 行内代码
    for m in LINK_RE.finditer(text):
        href = m.group(1)
        where = f"{rel(path)}: {href}"
        if href.startswith(("http://", "https://")):
            if strict_domains and not allowed_course_link(path, href):
                report.fail(f"{where} 非官方来源链接（仅允许 {', '.join(ALLOWED_DOMAINS)}）")
            else:
                report.ok("link", where)
            continue
        if href.startswith(("#", "mailto:")):
            continue
        target_part = unquote(href.split("#")[0])
        if href.startswith("/"):
            target = DOCS / target_part.lstrip("/")
        else:
            target = (path.parent / target_part).resolve()
        candidates = [target, target.with_suffix(".md") if target.suffix != ".md" else target, target / "index.md"]
        if any(c.exists() and (c.is_file()) for c in candidates):
            report.ok("link", where)
        else:
            report.fail(f"{where} 链接目标不存在")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--python", action="append", help="用于执行代码的解释器，可重复；默认当前解释器")
    ap.add_argument("-k", dest="pattern", help="只检查路径包含该片段的文件")
    ap.add_argument("-v", "--verbose", action="store_true", help="列出每一项通过的检查")
    args = ap.parse_args()
    pythons = args.python or [sys.executable]

    report = Report()
    seen_ids: dict[str, str] = {}
    course_files = sorted(COURSE.rglob("*.md"))
    other_docs = sorted(p for p in DOCS.rglob("*.md") if COURSE not in p.parents)
    if args.pattern:
        course_files = [p for p in course_files if args.pattern in str(p)]
        other_docs = [p for p in other_docs if args.pattern in str(p)]

    versions = []
    for py in pythons:
        out = subprocess.run([py, "-c", "import sys; print(sys.version.split()[0])"], capture_output=True, text=True)
        versions.append(f"{py} → Python {out.stdout.strip() or '?'}")
    print("解释器：\n  " + "\n  ".join(versions))
    print(f"文件：课程 {len(course_files)} 个，其他文档 {len(other_docs)} 个")

    all_blocks = []
    for f in course_files:
        check_structure(f, report)
        check_v21_lesson(f, report)
        check_links(f, report, strict_domains=True)
        all_blocks += parse_blocks(f)
    check_v21_duplicate_lines(course_files, report)
    check_v22_filler_markers(course_files, report)
    check_v22_duplicate_text(course_files, report)
    check_v22_duplicate_code_blocks(all_blocks, report)
    check_v22_pyodide_forbidden(all_blocks, report)
    check_v23_weak_run_blocks(all_blocks, report)
    check_v231_r6_unused_assignments(all_blocks, report)
    check_v232_r7_prewritten_prints(all_blocks, report)
    for f in other_docs:
        check_links(f, report, strict_domains=False)
        if f.name == "课程大纲.md":
            check_structure(f, report)
    check_blocks(all_blocks, pythons, report, seen_ids)

    if args.verbose:
        for p in report.passed:
            print("  ✓", p)
    n_browser_ex = report.counts.get("exercise", 0)
    n_local_ex = report.counts.get("local_exercise", 0)
    labels = {"example": "示例运行", "exercise": "练习参考答案通过（浏览器）", "local_exercise": "练习参考答案通过（本地）",
              "starter": "练习起始代码被判失败",
              "static": "静态代码语法", "source": "源码副本一致", "structure": "课程结构", "link": "链接",
              "v21_structure": "v2.1 量化结构", "v21_dup": "v2.1 重复行",
              "v22_filler": "v2.2 凑数清零", "v22_dup": "v2.2 正文查重",
              "v22_code_dup": "v2.2 代码块查重", "v22_pyodide": "v2.2 浏览器块",
              "v23_run_quality": "v2.3 弱示例门禁", "v231_r6": "v2.3.1 R6 未使用赋值",
              "v232_r7": "v2.3.2 R7 预写文字打印"}
    print("\n通过：")
    for k, label in labels.items():
        if report.counts.get(k):
            print(f"  {label}: {report.counts[k]}")
    if n_browser_ex or n_local_ex:
        print(f"  练习参考答案通过合计: {n_browser_ex + n_local_ex}（浏览器 {n_browser_ex} + 本地 {n_local_ex}）")
    n_ex = sum(1 for b in all_blocks if b.lang == "python" and "run" in b.flags)
    print(f"  （唯一示例 {n_ex} 个，唯一练习 {len(seen_ids)} 道，解释器 {len(pythons)} 个）")
    if report.failed:
        print(f"\n失败 {len(report.failed)} 项：")
        for f in report.failed:
            print("  ✗", f)
        return 1
    print("\n全部通过 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())

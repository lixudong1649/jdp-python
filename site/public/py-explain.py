"""Python 代码解读分析器：仅 ast/tokenize 分析，不执行用户代码。浏览器与 CPython 共用。"""

from __future__ import annotations

import ast
import json
import re
import sys
import tokenize
from io import BytesIO
from pathlib import Path
from typing import Any

try:
    ROOT = Path(__file__).resolve().parents[2]
except NameError:  # Pyodide runPython 无 __file__
    ROOT = Path(".")
CONCEPT_INDEX_PATH = ROOT / "docs" / "代码解读" / "概念索引.md"
MAX_LINES = 3000
MAX_BYTES = 400_000

STDLIB = getattr(sys, "stdlib_module_names", frozenset())

# 概念 id → AST 类型名（与概念索引「AST 节点或规则」列对齐，并补充语料常见节点）
AST_TO_CONCEPT: dict[str, str] = {
    "Module": "module",
    "FunctionDef": "function-def",
    "AsyncFunctionDef": "async-function-def",
    "ClassDef": "class-def",
    "Import": "import-statement",
    "ImportFrom": "from-import",
    "Assign": "assignment",
    "AnnAssign": "annotated-assign",
    "AugAssign": "aug-assign",
    "Return": "return-statement",
    "If": "if-statement",
    "For": "for-loop",
    "AsyncFor": "async-for",
    "While": "while-loop",
    "Break": "break-statement",
    "Continue": "continue-statement",
    "Pass": "pass-statement",
    "Raise": "raise-statement",
    "Try": "try-statement",
    "ExceptHandler": "except-handler",
    "With": "with-statement",
    "Assert": "assert-statement",
    "Delete": "del-statement",
    "Global": "global-statement",
    "Nonlocal": "nonlocal-statement",
    "Call": "call-expression",
    "Name": "name-reference",
    "Attribute": "attribute-access",
    "Subscript": "subscript",
    "Constant": "literal-constant",
    "List": "list-literal",
    "Tuple": "tuple-literal",
    "Dict": "dict-literal",
    "Set": "set-literal",
    "ListComp": "list-comprehension",
    "DictComp": "dict-comprehension",
    "SetComp": "set-comprehension",
    "GeneratorExp": "generator-expression",
    "JoinedStr": "f-string",
    "FormattedValue": "f-string",
    "Compare": "comparison",
    "BoolOp": "boolean-operator",
    "BinOp": "binary-operator",
    "UnaryOp": "unary-operator",
    "IfExp": "conditional-expression",
    "Lambda": "lambda-expression",
    "Starred": "starred-unpack",
    "NamedExpr": "walrus-operator",
    "Match": "match-statement",
    "match_case": "match-case",
    "Await": "await-expression",
    "Yield": "yield-expression",
    "YieldFrom": "yield-from",
    "Slice": "slice",
    "MatchAs": "match-case",
    "MatchClass": "match-case",
    "MatchMapping": "match-case",
    "MatchOr": "match-case",
    "MatchSequence": "match-case",
    "MatchStar": "match-case",
    "MatchValue": "match-case",
    "TypeAlias": "type-hint",
    "TypeVar": "type-hint",
    "withitem": "with-item",
}


def _load_concept_rows() -> list[dict[str, str]]:
    if not CONCEPT_INDEX_PATH.is_file():
        return []
    rows: list[dict[str, str]] = []
    for line in CONCEPT_INDEX_PATH.read_text(encoding="utf-8").splitlines():
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
        for token in re.split(r"[,、/|]", parts[2]):
            token = token.strip().replace("ast.", "")
            if token.endswith("*"):
                token = token[:-1]
            if token and token not in ("规则", "—"):
                AST_TO_CONCEPT.setdefault(token, parts[0])
    return rows


def _link_from_md(cell: str) -> list[str]:
    return re.findall(r"\]\(([^)]+)\)", cell)


def _concept_meta(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    meta: dict[str, dict[str, Any]] = {}
    for row in rows:
        meta[row["id"]] = {
            "name": row["name"],
            "meaning": row["meaning"],
            "course_links": _link_from_md(row["course"]),
            "glossary_links": _link_from_md(row["glossary"]),
        }
    return meta


def _syntax_error(source: str, exc: SyntaxError) -> dict[str, Any]:
    line = exc.lineno or 1
    col = exc.offset or 0
    msg = exc.msg or str(exc)
    hints = {
        "invalid syntax": "语法无效，检查括号、冒号或缩进是否成对",
        "unexpected EOF": "代码不完整，可能缺少括号或引号闭合",
        "expected ':'": "此处应有冒号（如 if/for/def 行末）",
    }
    zh = hints.get(msg, f"语法错误：{msg}")
    return {"ok": False, "error": {"line": line, "column": col, "message": zh}}


def _merge_lines(existing: list[int], new: int) -> list[int]:
    if new not in existing:
        existing.append(new)
    return sorted(existing)


class SyntaxRegistry:
    def __init__(self, concept_meta: dict[str, dict[str, Any]]) -> None:
        self.points: dict[str, dict[str, Any]] = {}
        self.concept_meta = concept_meta

    def add(self, syntax: str, line: int, concept_id: str, meaning: str | None = None) -> None:
        meta = self.concept_meta.get(concept_id, {})
        key = f"{syntax}|{concept_id}"
        if key not in self.points:
            self.points[key] = {
                "lines": [line],
                "syntax": syntax,
                "meaning": meaning or meta.get("meaning") or syntax,
                "concept_id": concept_id,
                "course_links": meta.get("course_links", []),
            }
        else:
            _merge_lines(self.points[key]["lines"], line)

    def to_list(self) -> list[dict[str, Any]]:
        return sorted(self.points.values(), key=lambda p: (min(p["lines"]), p["syntax"]))


class ExplainVisitor(ast.NodeVisitor):
    def __init__(self, registry: SyntaxRegistry, source: str) -> None:
        self.registry = registry
        self.source = source
        self.functions: list[dict[str, Any]] = []
        self.classes: list[dict[str, Any]] = []
        self.structure: list[dict[str, Any]] = []
        self.imports: list[dict[str, Any]] = []
        self.concept_ids: set[str] = set()
        self._loop_depth = 0
        self._for_has_break: dict[int, bool] = {}

    def visit_Import(self, node: ast.Import) -> None:
        names = [a.name for a in node.names]
        self.imports.append({"kind": "import", "module": names[0].split(".")[0], "names": names, "line": node.lineno})
        for alias in node.names:
            self.registry.add("import", node.lineno, "import-statement")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        mod = node.module or ""
        names = [a.name for a in node.names]
        self.imports.append(
            {"kind": "from", "module": mod.split(".")[0] if mod else "", "names": names, "line": node.lineno}
        )
        self.registry.add("from … import …", node.lineno, "from-import")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions.append({"name": node.name, "line": node.lineno, "is_async": False})
        has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
        syn = "def / return" if has_return else "def"
        self.registry.add(syn, node.lineno, "function-def")
        params = [a.arg for a in node.args.args]
        returns = [n.lineno for n in ast.walk(node) if isinstance(n, ast.Return) and n.lineno]
        call_names: set[str] = set()
        for n in ast.walk(node):
            if not isinstance(n, ast.Call):
                continue
            if isinstance(n.func, ast.Name):
                call_names.add(n.func.id)
            elif isinstance(n.func, ast.Attribute):
                call_names.add(n.func.attr)
        calls = sorted(call_names)
        self.structure.append(
            {
                "kind": "function",
                "name": node.name,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "params": params,
                "returns": returns,
                "docstring": ast.get_docstring(node) or "",
                "calls": [c for c in calls if isinstance(c, str)][:12],
            }
        )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.functions.append({"name": node.name, "line": node.lineno, "is_async": True})
        self.registry.add("async def", node.lineno, "async-function-def")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.append({"name": node.name, "line": node.lineno})
        self.registry.add("class", node.lineno, "class-def")
        self.structure.append(
            {
                "kind": "class",
                "name": node.name,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "docstring": ast.get_docstring(node) or "",
            }
        )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id.isupper():
                self.registry.add("全大写常量", node.lineno, "uppercase-constant")
            if isinstance(t, ast.Name):
                self.concept_ids.add("assignment")
        if isinstance(node.value, ast.Dict):
            self.registry.add("dict 字面量", node.lineno, "dict-literal")
        if isinstance(node.value, ast.List):
            self.registry.add("list 字面量", node.lineno, "list-literal")
        if isinstance(node.value, ast.Constant) and node.value.value is None:
            self.registry.add("None", node.lineno, "literal-constant")
        if isinstance(node.value, ast.Dict) and any(isinstance(v, ast.Name) for v in node.value.values):
            self.registry.add("函数作为值", node.lineno, "function-as-value")
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name) and node.target.id.isupper():
            self.registry.add("全大写常量", node.lineno, "uppercase-constant")
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        self.registry.add("return", node.lineno, "return-statement")
        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        self.registry.add("f-string", node.lineno, "f-string")
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self._loop_depth += 1
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
            self.registry.add("for + range", node.lineno, "for-loop")
        else:
            self.registry.add("for", node.lineno, "for-loop")
        self._for_has_break[id(node)] = False
        self.generic_visit(node)
        if node.orelse:
            self.registry.add("for … else", node.orelse[0].lineno, "for-else")
        self._loop_depth -= 1

    def visit_Break(self, node: ast.Break) -> None:
        self.registry.add("break", node.lineno, "break-statement")
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        if isinstance(node.test, ast.Compare):
            for op in node.test.ops:
                if isinstance(op, ast.NotEq):
                    self.registry.add("if + !=", node.lineno, "comparison")
        self.registry.add("if", node.lineno, "if-statement")
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        if any(isinstance(op, ast.NotEq) for op in node.ops):
            self.registry.add("!=", node.lineno, "comparison")
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        if isinstance(node.op, ast.Or):
            self.registry.add("or 取默认值", node.lineno, "boolean-operator")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        self.registry.add("下标访问", node.lineno, "subscript")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            self.registry.add("属性访问 / 方法调用", node.lineno, "attribute-access")
            if node.func.attr == "append":
                self.registry.add("list.append", node.lineno, "list-append")
            if node.func.attr == "join":
                self.registry.add("str.join", node.lineno, "str-join")
        if node.keywords:
            self.registry.add("关键字参数", node.lineno, "keyword-argument")
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self.registry.add("列表推导式", node.lineno, "list-comprehension")
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        self.registry.add("dict 字面量", node.lineno, "dict-literal")
        self.generic_visit(node)

    def visit_List(self, node: ast.List) -> None:
        self.registry.add("list 字面量", node.lineno, "list-literal")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if node.value is None:
            self.registry.add("None", node.lineno, "literal-constant")
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Call):
            self.registry.add("调用表达式", node.lineno, "call-expression")
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self.registry.add("lambda", node.lineno, "lambda-expression")
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self.registry.add("try", node.lineno, "try-statement")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.registry.add("except", node.lineno, "except-handler")
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        self.registry.add("with", node.lineno, "with-statement")
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self.registry.add(":= 海象运算符", node.lineno, "walrus-operator")
        self.generic_visit(node)


def _collect_comments(source: str, registry: SyntaxRegistry) -> None:
    try:
        tokens = tokenize.tokenize(BytesIO(source.encode("utf-8")).readline)
    except tokenize.TokenError:
        return
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            registry.add("注释", tok.start[0], "comment")


def _module_docstring(tree: ast.Module, registry: SyntaxRegistry) -> str | None:
    doc = ast.get_docstring(tree)
    if doc:
        end = doc.count("\n") + 1
        registry.add("文档字符串", 1, "docstring")
        if end > 1:
            registry.add("文档字符串", end, "docstring")
    return doc


def _has_main_guard(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            left = node.test.left
            if isinstance(left, ast.Name) and left.id == "__name__":
                return True
    return False


def _detect_starred_kwargs(node: ast.AST, registry: SyntaxRegistry) -> None:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            for kw in sub.keywords:
                if kw.arg is None:
                    registry.add("** 解包", sub.lineno, "starred-unpack")


def _run_info(imports: list[dict[str, Any]]) -> dict[str, Any]:
    blocked: list[str] = []
    third: list[str] = []
    for imp in imports:
        root = imp.get("module") or ""
        if not root or root.startswith("."):
            continue
        if root in STDLIB:
            continue
        third.append(root)
        blocked.append(root)
    can_browser = len(blocked) == 0
    uv_hint = f"uv add {' '.join(sorted(set(third)))}" if third else ""
    cmd = "uv run python your_script.py" if third else "在课程页点击运行，或：uv run python script.py"
    return {
        "can_run_in_browser": can_browser,
        "blocked_imports": sorted(set(blocked)),
        "third_party": sorted(set(third)),
        "uv_add_hint": uv_hint,
        "suggested_command": cmd,
    }


def _apply_pitfalls(tree: ast.AST, source: str, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    lines = source.splitlines()
    for rule in rules:
        rid = rule["id"]
        for line_no, snippet in rule["detect"](tree, lines):
            hits.append(
                {
                    "rule_id": rid,
                    "title": rule["title"],
                    "lines": [line_no],
                    "message": rule["message"],
                    "course_link": rule.get("course_link", ""),
                    "ruff_rule": rule.get("ruff_rule"),
                }
            )
    return hits


def _rule_mutable_default(tree: ast.AST, _lines: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults + node.args.kw_defaults:
                if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    out.append((node.lineno, "mutable default"))
    return out


def _rule_is_literal(tree: ast.AST, _lines: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op, comp in zip(node.ops, node.comparators, strict=False):
                if isinstance(op, (ast.Is, ast.IsNot)) and isinstance(comp, ast.Constant):
                    if isinstance(comp.value, (str, int, float, bool)):
                        out.append((node.lineno, "is literal"))
    return out


def _rule_bare_except(tree: ast.AST, _lines: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for h in node.handlers:
                if h.type is None:
                    out.append((h.lineno, "bare except"))
    return out


def _rule_none_eq(tree: ast.AST, _lines: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op, comp in zip(node.ops, node.comparators, strict=False):
                if isinstance(comp, ast.Constant) and comp.value is None and isinstance(op, (ast.Eq, ast.NotEq)):
                    out.append((node.lineno, "None compare"))
    return out


def _rule_wildcard_import(tree: ast.AST, _lines: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if any(a.name == "*" for a in node.names):
                out.append((node.lineno, "import *"))
    return out


def _rule_open_no_with(tree: ast.AST, _lines: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    with_lines = {n.lineno for n in ast.walk(tree) if isinstance(n, ast.With)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
            if node.lineno not in with_lines:
                out.append((node.lineno, "open()"))
    return out


def _rule_shadow_builtin(tree: ast.AST, _lines: list[str]) -> list[tuple[int, str]]:
    bad = {"list", "dict", "str", "int", "open", "input", "type", "id"}
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in bad:
            out.append((node.lineno, node.name))
    return out


def _rule_mutable_class_attr(tree: ast.AST, _lines: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, (ast.List, ast.Dict, ast.Set)):
                    out.append((stmt.lineno, "class mutable"))
    return out


def _rule_except_pass(tree: ast.AST, _lines: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for h in node.handlers:
                if len(h.body) == 1 and isinstance(h.body[0], ast.Pass):
                    out.append((h.lineno, "except pass"))
    return out


def _rule_assert_trivial(tree: ast.AST, lines: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert) and isinstance(node.test, ast.Constant) and node.test.value is True:
            out.append((node.lineno, "assert True"))
    return out


def _rule_len_bool(tree: ast.AST, _lines: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []

    def _is_len_call(node: ast.AST) -> bool:
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "len"

    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _is_len_call(node.test):
            out.append((node.lineno, "if len("))
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            if _is_len_call(node.test.left):
                out.append((node.lineno, "if len(...) compare"))
    return out


def _rule_duplicate_dict_key(tree: ast.AST, _lines: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys: list[Any] = []
            for k in node.keys:
                if isinstance(k, ast.Constant):
                    keys.append(k.value)
            if len(keys) != len(set(keys)):
                out.append((node.lineno, "dup key"))
    return out


PITFALL_RULES: list[dict[str, Any]] = [
    {
        "id": "mutable-default-arg",
        "title": "可变默认参数",
        "message": "列表/字典作默认参数会在多次调用间共享同一对象，改用 None 再在函数内创建。",
        "ruff_rule": "B006",
        "course_link": "../课程/03-控制流与函数/03-参数进阶与解包.md",
        "detect": _rule_mutable_default,
    },
    {
        "id": "is-literal-compare",
        "title": "用 is 比较字面量",
        "message": "is/is not 适合身份比较；与字符串、数字字面量比较应使用 ==。",
        "ruff_rule": "E712",
        "course_link": "../课程/04-容器/01-列表元组与切片.md",
        "detect": _rule_is_literal,
    },
    {
        "id": "bare-except",
        "title": "裸 except",
        "message": "except: 会捕获 SystemExit/KeyboardInterrupt，应写明异常类型。",
        "ruff_rule": "E722",
        "course_link": "../课程/06-异常/02-try-except-raise.md",
        "detect": _rule_bare_except,
    },
    {
        "id": "none-equality",
        "title": "用 == 判断 None",
        "message": "判断 None 推荐 `is None` / `is not None`，避免与重载 __eq__ 的对象混淆。",
        "ruff_rule": "E711",
        "course_link": "../课程/02-基础语法与数据类型/02-数字布尔与None.md",
        "detect": _rule_none_eq,
    },
    {
        "id": "wildcard-import",
        "title": "通配符 import",
        "message": "from module import * 污染命名空间，难以追踪名字来源。",
        "ruff_rule": "F403",
        "course_link": "../课程/05-模块与包/01-模块与import.md",
        "detect": _rule_wildcard_import,
    },
    {
        "id": "open-no-with",
        "title": "open 未配合 with",
        "message": "直接 open() 容易忘记 close；推荐 with open(...) as f。",
        "ruff_rule": "SIM115",
        "course_link": "../课程/06-异常/03-with与上下文管理器.md",
        "detect": _rule_open_no_with,
    },
    {
        "id": "shadow-builtin",
        "title": "函数名遮蔽内置名",
        "message": "把函数命名为 list/open 等会使内置名在本作用域不可用。",
        "ruff_rule": "A001",
        "course_link": "../课程/03-控制流与函数/02-函数定义与调用.md",
        "detect": _rule_shadow_builtin,
    },
    {
        "id": "mutable-class-attribute",
        "title": "类属性共享可变对象",
        "message": "类级别的 list/dict 会被所有实例共享，实例属性请放在 __init__。",
        "ruff_rule": "B006",
        "course_link": "../课程/07-类与对象/01-类与实例.md",
        "detect": _rule_mutable_class_attr,
    },
    {
        "id": "except-pass",
        "title": "except 后只 pass",
        "message": "吞掉异常会隐藏错误；至少记录日志或重新抛出。",
        "ruff_rule": "S110",
        "course_link": "../课程/06-异常/02-try-except-raise.md",
        "detect": _rule_except_pass,
    },
    {
        "id": "assert-trivial",
        "title": "无意义的 assert True",
        "message": "assert True 不能检查任何条件，应写真实断言或删除。",
        "ruff_rule": "B011",
        "course_link": "../课程/15-测试/01-pytest基础.md",
        "detect": _rule_assert_trivial,
    },
    {
        "id": "len-as-bool",
        "title": "用 if len(x) 判空",
        "message": "空容器可直接 `if not xs`；仅在需要区分 None 与空容器时再比长度。",
        "ruff_rule": "PLC1802",
        "course_link": "../课程/04-容器/01-列表元组与切片.md",
        "detect": _rule_len_bool,
    },
    {
        "id": "duplicate-key-dict-literal",
        "title": "字典字面量重复键",
        "message": "重复键后者覆盖前者，通常是笔误。",
        "ruff_rule": "F601",
        "course_link": "../课程/04-容器/02-字典.md",
        "detect": _rule_duplicate_dict_key,
    },
]

PITFALL_SELFTEST: dict[str, dict[str, list[str]]] = {
    "mutable-default-arg": {
        "should_hit": ["def f(a=[]):\n    return a\n", "def g(x, m={}):\n    return m\n"],
        "should_miss": ["def f(a=None):\n    a = a or []\n    return a\n", "def g(x=1):\n    return x\n"],
    },
    "is-literal-compare": {
        "should_hit": ["if x is 'a':\n    pass\n", "if y is not 0:\n    pass\n"],
        "should_miss": ["if x == 'a':\n    pass\n", "if y is None:\n    pass\n"],
    },
    "bare-except": {
        "should_hit": ["try:\n    1/0\nexcept:\n    pass\n", "try:\n    f()\nexcept:\n    x=1\n"],
        "should_miss": ["try:\n    1/0\nexcept ZeroDivisionError:\n    pass\n", "try:\n    f()\nexcept ValueError:\n    pass\n"],
    },
    "none-equality": {
        "should_hit": ["if x == None:\n    pass\n", "if y != None:\n    pass\n"],
        "should_miss": ["if x is None:\n    pass\n", "if y is not None:\n    pass\n"],
    },
    "wildcard-import": {
        "should_hit": ["from os import *\n", "from math import *\n"],
        "should_miss": ["from os import path\n", "import os\n"],
    },
    "open-no-with": {
        "should_hit": ["f = open('a.txt')\n", "open('b.txt').read()\n"],
        "should_miss": ["with open('a.txt') as f:\n    f.read()\n", "import io\nbuf = io.StringIO()\n"],
    },
    "shadow-builtin": {
        "should_hit": ["def list():\n    return 1\n", "def open():\n    pass\n"],
        "should_miss": ["def mylist():\n    return 1\n", "def load():\n    pass\n"],
    },
    "mutable-class-attribute": {
        "should_hit": ["class A:\n    xs = []\n", "class B:\n    m = {}\n"],
        "should_miss": ["class A:\n    x = 1\n", "class B:\n    def __init__(self):\n        self.m = {}\n"],
    },
    "except-pass": {
        "should_hit": ["try:\n    f()\nexcept ValueError:\n    pass\n", "try:\n    g()\nexcept TypeError:\n    pass\n"],
        "should_miss": ["try:\n    f()\nexcept ValueError as e:\n    raise e\n", "try:\n    g()\nexcept TypeError:\n    print('ok')\n"],
    },
    "assert-trivial": {
        "should_hit": ["assert True\n", "def f():\n    assert True\n"],
        "should_miss": ["assert x > 0\n", "assert isinstance(x, int)\n"],
    },
    "len-as-bool": {
        "should_hit": ["if len(items):\n    pass\n", "if len(x) == 0:\n    pass\n"],
        "should_miss": ["if not items:\n    pass\n", "if items:\n    pass\n"],
    },
    "duplicate-key-dict-literal": {
        "should_hit": ["d = {'a': 1, 'a': 2}\n", "m = {1: 'x', 1: 'y'}\n"],
        "should_miss": ["d = {'a': 1, 'b': 2}\n", "m = {1: 'x', 2: 'y'}\n"],
    },
}


def explain(source: str, filename: str = "<input>") -> dict[str, Any]:
    if len(source.encode("utf-8")) > MAX_BYTES:
        return {
            "ok": False,
            "error": {"line": 1, "column": 0, "message": "代码超过 400 KB 上限，请缩短后再解读"},
        }
    line_count = len(source.splitlines())
    if line_count > MAX_LINES:
        return {
            "ok": False,
            "error": {"line": 1, "column": 0, "message": f"代码超过 {MAX_LINES} 行上限，请缩短后再解读"},
        }
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return _syntax_error(source, exc)

    rows = _load_concept_rows()
    concept_meta = _concept_meta(rows)
    registry = SyntaxRegistry(concept_meta)
    doc = _module_docstring(tree, registry)
    _collect_comments(source, registry)
    visitor = ExplainVisitor(registry, source)
    visitor.visit(tree)
    _detect_starred_kwargs(tree, registry)

    syntax_points = registry.to_list()
    if not syntax_points:
        syntax_points = [
            {
                "lines": [1],
                "syntax": "模块",
                "meaning": "可执行的 Python 模块",
                "concept_id": "module",
                "course_links": [],
            }
        ]

    concept_ids: set[str] = set(p["concept_id"] for p in syntax_points)
    for node in ast.walk(tree):
        name = type(node).__name__
        cid = AST_TO_CONCEPT.get(name)
        if cid:
            concept_ids.add(cid)

    concepts_out: list[dict[str, Any]] = []
    for cid in sorted(concept_ids):
        meta = concept_meta.get(cid, {"name": cid, "meaning": cid, "course_links": [], "glossary_links": []})
        concepts_out.append(
            {
                "id": cid,
                "name": meta.get("name", cid),
                "course_links": meta.get("course_links", []),
                "glossary_links": meta.get("glossary_links", []),
            }
        )

    overview = {
        "line_count": line_count,
        "docstring": doc,
        "imports": visitor.imports,
        "functions": visitor.functions,
        "classes": visitor.classes,
        "top_level_summary": _top_level_summary(tree),
        "has_main_guard": _has_main_guard(tree),
    }

    return {
        "ok": True,
        "overview": overview,
        "syntax_points": syntax_points,
        "structure": visitor.structure,
        "concepts": concepts_out,
        "run_info": _run_info(visitor.imports),
        "pitfalls": _apply_pitfalls(tree, source, PITFALL_RULES),
    }


def _top_level_summary(tree: ast.Module) -> str:
    parts: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            parts.append(f"定义函数 {node.name}")
        elif isinstance(node, ast.ClassDef):
            parts.append(f"定义类 {node.name}")
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if names:
                parts.append(f"赋值 {', '.join(names[:3])}")
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            parts.append("顶层表达式调用")
    return "；".join(parts[:8]) if parts else "仅包含导入或声明"


def configure(concept_index_path: str | None = None) -> None:
    """浏览器 Worker 可指定概念索引路径（默认读仓库 docs/）。"""
    global CONCEPT_INDEX_PATH
    if concept_index_path:
        CONCEPT_INDEX_PATH = Path(concept_index_path)


def course_explain(source: str, filename: str = "<input>") -> dict[str, Any]:
    """Pyodide Worker 入口，与 course_run 相同返回 dict。"""
    return explain(source, filename=filename)


if __name__ == "__main__" and "--cli" in sys.argv:
    idx = sys.argv.index("--cli") + 1
    path = sys.argv[idx]
    code = Path(path).read_text(encoding="utf-8")
    print(json.dumps(explain(code, filename=Path(path).name), ensure_ascii=False))

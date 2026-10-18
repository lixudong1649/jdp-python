"""课程质量校验器：执行 docs/课程 中的全部示例与练习，并检查结构、链接与版本标注。

用法（项目根目录）：
    uv run python tests/check_course.py               # 用项目解释器（.python-version = 3.12）
    python3 tests/check_course.py --python python3.14 # 指定其他解释器，可重复传入多个
    python3 tests/check_course.py -k 03-函数          # 只检查路径包含该片段的文件

代码块约定（与 site/.vitepress/lib/blocks.mjs 一致）：
    ```python run                    可运行示例，必须无异常结束
    ```python run raises=TypeError   预期抛出指定异常
    ```python exercise id=<ID>       练习：# --- starter --- / # --- solution --- / # --- check --- 三段
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
        if "run" in b.flags or "local" in b.flags:
            for py in pythons:
                jobs.append((where, ("raises", b.attrs["raises"]) if "raises" in b.attrs else ("ok", None), py, b.content, "", "example"))
        elif "exercise" in b.flags:
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
            for py in pythons:
                jobs.append((f"{where} [{ex_id}] solution", ("ok", None), py, ex["solution"], ex["check"], "exercise"))
                jobs.append((f"{where} [{ex_id}] starter", ("fail", None), py, ex["starter"], ex["check"], "starter"))
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
    r"concurrent\.futures|ThreadPoolExecutor|ProcessPoolExecutor",
    re.I,
)


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
    n_ex = len(re.findall(r"```python exercise", text))
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
        if "run" not in b.flags and "exercise" not in b.flags:
            continue
        if not PYODIDE_FORBIDDEN_IN_RUN.search(b.content):
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
        if "```python exercise" not in text:
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
    for f in other_docs:
        check_links(f, report, strict_domains=False)
        if f.name == "课程大纲.md":
            check_structure(f, report)
    check_blocks(all_blocks, pythons, report, seen_ids)

    if args.verbose:
        for p in report.passed:
            print("  ✓", p)
    labels = {"example": "示例运行", "exercise": "练习参考答案通过", "starter": "练习起始代码被判失败",
              "static": "静态代码语法", "source": "源码副本一致", "structure": "课程结构", "link": "链接",
              "v21_structure": "v2.1 量化结构", "v21_dup": "v2.1 重复行",
              "v22_filler": "v2.2 凑数清零", "v22_dup": "v2.2 正文查重",
              "v22_code_dup": "v2.2 代码块查重", "v22_pyodide": "v2.2 浏览器块"}
    print("\n通过：")
    for k, label in labels.items():
        if report.counts.get(k):
            print(f"  {label}: {report.counts[k]}")
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

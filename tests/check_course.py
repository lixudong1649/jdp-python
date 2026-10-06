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
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
COURSE = DOCS / "课程"
RUNTIME = ROOT / "site" / "public" / "py-runtime.py"

LESSON_SECTIONS = ["目标", "核心概念", "易错点", "对照", "读代码", "练习", "小结", "延伸阅读"]
ALLOWED_DOMAINS = ("docs.python.org", "peps.python.org", "docs.astral.sh", "packaging.python.org")
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
        if "run" in b.flags:
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


def check_links(path: Path, report: Report, strict_domains: bool) -> None:
    text = path.read_text(encoding="utf-8")
    # 去掉代码块，避免把代码中的方括号当作链接
    text = re.sub(r"^(`{3,}).*?^\1\s*$", "", text, flags=re.M | re.S)
    text = re.sub(r"`[^`\n]+`", "", text)  # 行内代码
    for m in LINK_RE.finditer(text):
        href = m.group(1)
        where = f"{rel(path)}: {href}"
        if href.startswith(("http://", "https://")):
            host = re.sub(r"^https?://([^/]+).*$", r"\1", href)
            if strict_domains and not host.endswith(ALLOWED_DOMAINS):
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
        check_links(f, report, strict_domains=True)
        all_blocks += parse_blocks(f)
    for f in other_docs:
        check_links(f, report, strict_domains=False)
        if f.name == "课程大纲.md":
            check_structure(f, report)
    check_blocks(all_blocks, pythons, report, seen_ids)

    if args.verbose:
        for p in report.passed:
            print("  ✓", p)
    labels = {"example": "示例运行", "exercise": "练习参考答案通过", "starter": "练习起始代码被判失败",
              "static": "静态代码语法", "source": "源码副本一致", "structure": "课程结构", "link": "链接"}
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

"""课程代码运行时：浏览器（Pyodide Web Worker）与本地校验器（tests/check_course.py）共用。

course_run(code, check) 在全新命名空间中执行 code（__name__ == "__main__"），
如给出 check，则在同一命名空间中继续执行检查代码（练习判题）。
每次运行都在临时目录中进行，结束后恢复工作目录、sys.path，并清理本次新导入的临时模块与 logging 配置。
"""

import io
import json
import linecache
import os
import shutil
import sys
import tempfile
import time
import traceback

MAX_OUTPUT = 20_000


def _format_error(exc: BaseException, filename: str) -> str:
    if isinstance(exc, AssertionError) and filename == "check.py":
        msg = str(exc).strip()
        if msg:
            return f"检查未通过：{msg}"
        tb = exc.__traceback__
        while tb and tb.tb_next:
            tb = tb.tb_next
        line = linecache.getline("check.py", tb.tb_lineno).strip() if tb else ""
        return f"检查未通过：断言失败 {line}"
    tb = exc.__traceback__
    # 跳过运行时自身的栈帧，只保留用户代码相关部分
    while tb is not None and tb.tb_frame.f_code.co_filename not in ("main.py", "check.py"):
        tb = tb.tb_next
    return "".join(traceback.format_exception(type(exc), exc, tb))


def _exec(code: str, filename: str, ns: dict):
    linecache.cache[filename] = (len(code), None, code.splitlines(True), filename)
    try:
        exec(compile(code, filename, "exec"), ns)
    except SystemExit as exc:
        if exc.code not in (None, 0):
            return False, f"SystemExit: {exc.code}", "SystemExit"
    except BaseException as exc:  # noqa: BLE001 - 需要把任何错误展示给学习者
        return False, _format_error(exc, filename), type(exc).__name__
    return True, "", ""


def _reset_logging():
    logging = sys.modules.get("logging")
    if logging is None:
        return
    for logger in [logging.getLogger(), *logging.Logger.manager.loggerDict.values()]:
        if isinstance(logger, logging.Logger):
            for h in list(logger.handlers):
                logger.removeHandler(h)
            logger.setLevel(logging.NOTSET)
            logger.propagate = True
            logger.disabled = False
    logging.getLogger().setLevel(logging.WARNING)


def course_run(code: str, check: str = "") -> dict:
    buf = io.StringIO()
    ns = {"__name__": "__main__", "__builtins__": __builtins__}
    old_out, old_err, old_cwd, old_path = sys.stdout, sys.stderr, os.getcwd(), list(sys.path)
    old_modules = set(sys.modules)
    workdir = tempfile.mkdtemp(prefix="course-")
    os.chdir(workdir)
    sys.path.insert(0, workdir)
    sys.stdout = sys.stderr = buf
    start = time.perf_counter()
    phase, err, err_type = "", "", ""
    try:
        ok, err, err_type = _exec(code, "main.py", ns)
        if not ok:
            phase = "code"
        elif check.strip():
            ok, err, err_type = _exec(check, "check.py", ns)
            if not ok:
                phase = "check"
    finally:
        sys.stdout, sys.stderr = old_out, old_err
        os.chdir(old_cwd)
        sys.path[:] = old_path
        for name in set(sys.modules) - old_modules:
            mod_file = getattr(sys.modules.get(name), "__file__", None) or ""
            if mod_file.startswith(workdir):
                del sys.modules[name]
        _reset_logging()
        shutil.rmtree(workdir, ignore_errors=True)
    out = buf.getvalue()
    if len(out) > MAX_OUTPUT:
        out = out[:MAX_OUTPUT] + "\n…（输出过长，已截断）"
    return {
        "ok": ok,
        "out": out,
        "err": err,
        "errType": err_type,
        "phase": phase,
        "ms": round((time.perf_counter() - start) * 1000),
        "python": sys.version.split()[0],
    }


if __name__ == "__main__" and "--cli" in sys.argv:
    # 本地校验器调用：python py-runtime.py --cli <code.py> [check.py]，结果以 JSON 输出到 stdout
    args = sys.argv[sys.argv.index("--cli") + 1 :]
    code_src = open(args[0], encoding="utf-8").read()
    check_src = open(args[1], encoding="utf-8").read() if len(args) > 1 else ""
    print(json.dumps(course_run(code_src, check_src), ensure_ascii=False))

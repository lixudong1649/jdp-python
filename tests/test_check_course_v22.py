"""v2.2 课程门禁：归一化查重、凑数标记、浏览器块与代码块查重。"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from check_course import (
    COURSE,
    Block,
    Report,
    _normalize_code_block,
    check_blocks,
    check_v22_duplicate_code_blocks,
    check_v22_duplicate_text,
    check_v22_filler_markers,
    check_v22_pyodide_forbidden,
    normalize_v22_text,
    pyodide_forbidden_in_block,
)


class NormalizeV22Test(unittest.TestCase):
    def test_strips_lesson_specific_parts(self):
        a = "自测题（docs/课程/18-并发/02.md·0）：若让你向同事用三分钟讲清「18.2 futures」的核心差别"
        b = "自测题（docs/课程/19-asyncio/01.md·99）：若让你向同事用三分钟讲清「19.1 协程」的核心差别"
        self.assertEqual(normalize_v22_text(a), normalize_v22_text(b))

    def test_code_normalize_drops_comments_and_blank_lines(self):
        a = "import os\nx = 1  # hi\n"
        b = "import os\n\nx = 1\n"
        self.assertEqual(_normalize_code_block(a), _normalize_code_block(b))


class V22GatesTest(unittest.TestCase):
    def test_filler_marker_detected(self):
        report = Report()
        with tempfile.TemporaryDirectory() as tmp:
            course = Path(tmp) / "课程"
            probe = course / "12-数据模型与协议" / "99-gate-probe.md"
            probe.parent.mkdir(parents=True)
            probe.write_text("---\ntitle: probe\n---\n# probe\n课堂延展\n", encoding="utf-8")
            with mock.patch("check_course.COURSE", course):
                check_v22_filler_markers([probe], report)
        self.assertTrue(report.failed)

    def test_pyodide_forbidden_threading(self):
        report = Report()
        fake = COURSE / "18-并发" / "01-threading与GIL.md"
        blocks = [
            Block(fake, 1, "python", {"run"}, {}, "import threading\nprint(1)\n"),
        ]
        check_v22_pyodide_forbidden(blocks, report)
        self.assertTrue(report.failed)

    def test_pyodide_allows_local_flag_same_content(self):
        report = Report()
        fake = COURSE / "18-并发" / "01-threading与GIL.md"
        blocks = [
            Block(fake, 1, "python", {"local"}, {}, "import threading\nprint(1)\n"),
        ]
        check_v22_pyodide_forbidden(blocks, report)
        self.assertFalse(report.failed)

    def test_duplicate_code_blocks_across_lessons(self):
        report = Report()
        a = COURSE / "18-并发" / "02-multiprocessing与futures.md"
        b = COURSE / "18-并发" / "03-free-threaded现状.md"
        code = "import threading\nlock = threading.Lock()\nprint('ok')\n"
        blocks = [
            Block(a, 10, "python", {"run"}, {}, code),
            Block(b, 20, "python", {"run"}, {}, code),
        ]
        check_v22_duplicate_code_blocks(blocks, report)
        self.assertTrue(report.failed)

    def test_duplicate_text_template_sentence(self):
        report = Report()
        p = COURSE / "12-数据模型与协议" / "01-特殊方法全景.md"
        if not p.exists():
            self.skipTest("课程文件不存在")
        check_v22_duplicate_text([p], report)
        # 单课不会触发跨课；只验证不崩溃
        self.assertIsInstance(report.failed, list)


class LocalExerciseGradingTest(unittest.TestCase):
    _FAKE = COURSE / "18-并发" / "01-threading与GIL.md"

    def test_local_exercise_solution_must_pass(self):
        body = """# --- starter ---
def f():
    return 0
# --- solution ---
def f():
    return 1
# --- check ---
assert f() == 1
"""
        blocks = [
            Block(self._FAKE, 1, "python", {"local", "exercise"}, {"id": "probe-sol"}, body),
        ]
        report = Report()
        check_blocks(blocks, [sys.executable], report, {})
        self.assertFalse(any("probe-sol" in f for f in report.failed))
        self.assertGreaterEqual(report.counts.get("local_exercise", 0), 1)

    def test_local_exercise_starter_must_fail(self):
        body = """# --- starter ---
def f():
    return 1
# --- solution ---
def f():
    return 1
# --- check ---
assert f() == 1
"""
        blocks = [
            Block(self._FAKE, 1, "python", {"local", "exercise"}, {"id": "probe-starter"}, body),
        ]
        report = Report()
        check_blocks(blocks, [sys.executable], report, {})
        self.assertTrue(any("starter 竟然通过" in f for f in report.failed))


class PyodideConcurrentFuturesTest(unittest.TestCase):
    def test_executor_imports_forbidden_in_run(self):
        samples = [
            "from concurrent.futures import ThreadPoolExecutor\n",
            "from concurrent.futures import ProcessPoolExecutor\n",
            "from concurrent.futures import as_completed\n",
        ]
        for code in samples:
            self.assertTrue(pyodide_forbidden_in_block(code), msg=code)

    def test_future_import_allowed(self):
        self.assertFalse(
            pyodide_forbidden_in_block("from concurrent.futures import Future\nf = Future()\n")
        )

    def test_as_completed_forbidden_in_exercise_block(self):
        report = Report()
        fake = COURSE / "18-并发" / "01-threading与GIL.md"
        blocks = [
            Block(
                fake,
                1,
                "python",
                {"run", "exercise"},
                {"id": "x"},
                "from concurrent.futures import as_completed\n",
            ),
        ]
        check_v22_pyodide_forbidden(blocks, report)
        self.assertTrue(report.failed)


if __name__ == "__main__":
    unittest.main()

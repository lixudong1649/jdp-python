"""v2.3 弱示例门禁 R1–R5。"""
import unittest

from check_course import (
    COURSE,
    Block,
    Report,
    _effective_code_lines,
    _run_block_import_print_only,
    check_v23_weak_run_blocks,
)


class V23EffectiveLinesTest(unittest.TestCase):
    def test_strips_comments_and_blanks(self):
        code = "x = 1  # comment\n\ny = 2\n"
        self.assertEqual(_effective_code_lines(code), ["x = 1", "y = 2"])


class V23GatesTest(unittest.TestCase):
    _FAKE = COURSE / "14-文本文件与命令行" / "01-编码与bytes.md"

    def test_r1_short_run_block(self):
        report = Report()
        blocks = [
            Block(self._FAKE, 1, "python", {"run"}, {}, "a = 1\nprint(a)\n"),
        ]
        check_v23_weak_run_blocks(blocks, report)
        self.assertTrue(any("v2.3 R1" in f for f in report.failed))

    def test_r2_import_print_only(self):
        report = Report()
        blocks = [
            Block(
                self._FAKE,
                1,
                "python",
                {"run"},
                {},
                "import sys\nprint(sys.version)\n",
            ),
        ]
        check_v23_weak_run_blocks(blocks, report)
        self.assertTrue(any("v2.3 R2" in f for f in report.failed))

    def test_r3_short_raises_block(self):
        report = Report()
        blocks = [
            Block(self._FAKE, 1, "python", {"run"}, {"raises": "ValueError"}, "raise ValueError\n"),
        ]
        check_v23_weak_run_blocks(blocks, report)
        self.assertTrue(any("v2.3 R3" in f for f in report.failed))

    def test_r4_similar_run_blocks(self):
        report = Report()
        code_a = (
            "def validate_limit(limit: int) -> int:\n"
            "    if limit < 1 or limit > 100:\n"
            "        raise ValueError('bad')\n"
            "    return limit\n"
            "print(validate_limit(10))\n"
        )
        code_b = (
            "def validate_limit(limit: int) -> int:\n"
            "    if limit < 1 or limit > 100:\n"
            "        raise ValueError('bad')\n"
            "    return limit\n"
            "print(validate_limit(5))\n"
        )
        blocks = [
            Block(self._FAKE, 10, "python", {"run"}, {}, code_a),
            Block(self._FAKE, 20, "python", {"run"}, {}, code_b),
        ]
        check_v23_weak_run_blocks(blocks, report)
        self.assertTrue(any("v2.3 R4" in f for f in report.failed))

    def test_r5_or_true(self):
        report = Report()
        blocks = [
            Block(
                self._FAKE,
                1,
                "python",
                {"run"},
                {},
                "x = 1\nassert x == 1 or True\nprint(x)\nprint(2)\nprint(3)\n",
            ),
        ]
        check_v23_weak_run_blocks(blocks, report)
        self.assertTrue(any("v2.3 R5" in f for f in report.failed))

    def test_import_print_only_helper(self):
        self.assertTrue(_run_block_import_print_only("import os\nprint(1)\n"))
        self.assertFalse(_run_block_import_print_only("x = 1\nprint(x)\n"))


if __name__ == "__main__":
    unittest.main()

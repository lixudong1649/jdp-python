"""v2.3.2：R7 预写文字打印门禁。"""
import unittest

from check_course import (
    COURSE,
    Block,
    Report,
    ROOT,
    check_v232_r7_prewritten_prints,
    nth_python_run_block,
    prewritten_print_counts,
    run_block_fails_v232_r7,
)


class V232R7HelperTest(unittest.TestCase):
    def test_three_literal_prints_fail(self):
        code = 'print("a")\nprint("b")\nprint("c")\n'
        self.assertTrue(run_block_fails_v232_r7(code))

    def test_mixed_prints_pass(self):
        code = (
            "x = len('ab')\n"
            "y = x + 1\n"
            'print("a")\n'
            "print(x)\n"
            "print(y)\n"
        )
        self.assertFalse(run_block_fails_v232_r7(code))

    def test_two_prints_not_checked(self):
        code = 'print("only")\nprint("two")\n'
        total, literal = prewritten_print_counts(code)
        self.assertEqual((total, literal), (2, 2))
        self.assertFalse(run_block_fails_v232_r7(code))

    def test_hasattr_arg_still_prewritten(self):
        code = (
            "import asyncio\n"
            'print("taskgroup", hasattr(asyncio, "TaskGroup"))\n'
            'print("again", hasattr(asyncio, "gather"))\n'
            'print("third", "literal")\n'
        )
        self.assertTrue(run_block_fails_v232_r7(code))


class V232R7TargetBlocksTest(unittest.TestCase):
    def test_t1_t2_t3_pass_after_rewrite(self):
        specs = [
            ("docs/课程/19-asyncio/02-gather与TaskGroup.md", 2),
            ("docs/课程/17-打包与发布/03-发布流程.md", 4),
            ("docs/课程/14-文本文件与命令行/01-编码与bytes.md", 9),
        ]
        still_weak = []
        for rel_path, index in specs:
            block = nth_python_run_block(ROOT / rel_path, index)
            if run_block_fails_v232_r7(block.content):
                still_weak.append(f"{rel_path} run#{index}")
        self.assertEqual(still_weak, [], "T1–T3 改写后应通过 R7：\n" + "\n".join(still_weak))

    def test_r7_gate_reports_failure(self):
        report = Report()
        code = 'print("a")\nprint("b")\nprint("c")\n'
        check_v232_r7_prewritten_prints(
            [
                Block(
                    COURSE / "14-文本文件与命令行" / "01-编码与bytes.md",
                    1,
                    "python",
                    {"run"},
                    {},
                    code,
                )
            ],
            report,
        )
        self.assertTrue(any("v2.3.2 R7" in f for f in report.failed))


if __name__ == "__main__":
    unittest.main()

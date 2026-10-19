"""v2.3.1：R6 未使用赋值与 13 个目标 run 块有效行数回归。"""
import unittest
from pathlib import Path

from check_course import (
    ROOT,
    V231_MIN_REGRESSION_EFFECTIVE,
    V231_RUN_BLOCK_SPECS,
    _effective_code_lines,
    nth_python_run_block,
    unused_assigned_variables,
)


class V231R6Test(unittest.TestCase):
    def test_detects_header_like_14_1_run_block_2_before_fix(self):
        # M1 时 14.1 第 2 个 run 块含未读的 header；用同结构片段回归 R6 逻辑
        code = (
            'header = b"GET "\n'
            "payload = bytearray(b'index.html')\n"
            "print(bytes(payload))\n"
        )
        names = [n for n, _ in unused_assigned_variables(code)]
        self.assertIn("header", names)


class V231RegressionLinesTest(unittest.TestCase):
    def test_target_run_blocks_have_eight_effective_lines(self):
        short: list[str] = []
        for rel_path, index in V231_RUN_BLOCK_SPECS:
            block = nth_python_run_block(ROOT / rel_path, index)
            n = len(_effective_code_lines(block.content))
            if n < V231_MIN_REGRESSION_EFFECTIVE:
                short.append(f"{rel_path} run#{index} @ {block.line}: {n} 行")
        self.assertEqual(
            short,
            [],
            "以下块有效代码不足 8 行：\n" + "\n".join(short),
        )


if __name__ == "__main__":
    unittest.main()

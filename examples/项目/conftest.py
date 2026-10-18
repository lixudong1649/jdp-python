"""为各阶段项目测试注入模块搜索路径（每个 NN-名称 目录可独立 import 同级 .py）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for child in ROOT.iterdir():
    if child.is_dir() and child.name[:2].isdigit():
        sys.path.insert(0, str(child))

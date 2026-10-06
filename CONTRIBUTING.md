# 反馈与贡献

## 反馈问题

请在 [GitHub Issues](https://github.com/lixudong1649/jdp-python/issues) 提交，并写明：

- 页面或文件路径（如 `docs/课程/04-容器/02-字典.md` 或网站链接）
- 问题类型：事实错误 / 表述不清 / 过时信息 / 代码无法运行 / 网站问题
- 期望的修改，以及依据（官方文档链接、Python 版本）

## 修改内容

1. 只改 `docs/` 下的 Markdown；代码块约定见 `site/.vitepress/lib/blocks.mjs` 文件头。
2. 提交前本地校验：

   ```bash
   uv run python tests/check_course.py
   cd site && npm ci && npm run verify:pyodide && npm run build
   ```

3. 不要提交 `.env`、密钥或个人信息；涉及版本的事实请标注核对日期。

提交即表示同意按 [LICENSE](LICENSE)（代码，MIT）与 [LICENSE-CONTENT.md](LICENSE-CONTENT.md)（课程内容，CC BY-NC-SA 4.0）授权。

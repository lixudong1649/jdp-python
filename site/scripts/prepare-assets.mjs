// 构建/开发前准备静态资源：
// 1. 把 node_modules/pyodide 的核心文件复制到 public/pyodide/（本地离线运行 Python，无需 CDN）；
// 2. 把 docs/ 引用到的仓库文件（examples/、README.md、pyproject.toml）复制为 public/repo/**.txt 纯文本副本。
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const project = path.resolve(site, '..')

const pyodideSrc = path.join(site, 'node_modules/pyodide')
const pyodideDst = path.join(site, 'public/pyodide')
const files = ['pyodide.mjs', 'pyodide.asm.mjs', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json']
fs.mkdirSync(pyodideDst, { recursive: true })
let copied = 0
for (const f of files) {
  const src = path.join(pyodideSrc, f)
  if (!fs.existsSync(src)) { console.warn(`[prepare-assets] 缺少 ${f}，浏览器将回退到 CDN`); continue }
  fs.copyFileSync(src, path.join(pyodideDst, f))
  copied++
}
console.log(`[prepare-assets] pyodide: ${copied}/${files.length} 个文件 -> public/pyodide/`)

const repoDst = path.join(site, 'public/repo')
fs.rmSync(repoDst, { recursive: true, force: true })
const copyText = (rel) => {
  const src = path.join(project, rel)
  if (!fs.existsSync(src)) return 0
  const dst = path.join(repoDst, rel + '.txt')
  fs.mkdirSync(path.dirname(dst), { recursive: true })
  fs.copyFileSync(src, dst)
  return 1
}
let n = 0
const walk = (rel) => {
  for (const e of fs.readdirSync(path.join(project, rel), { withFileTypes: true })) {
    const r = path.join(rel, e.name)
    if (e.isDirectory()) { if (e.name !== '__pycache__') walk(r) }
    else if (/\.(py|md)$/.test(e.name)) n += copyText(r)
  }
}
if (fs.existsSync(path.join(project, 'examples'))) walk('examples')
for (const f of ['README.md', 'pyproject.toml']) n += copyText(f)
console.log(`[prepare-assets] repo: ${n} 个文件 -> public/repo/`)

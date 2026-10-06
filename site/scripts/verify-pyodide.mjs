// 在 Node 中用 Pyodide（与浏览器相同的运行时与 py-runtime.py）执行全部课程代码块：
//   示例（run）必须正常结束或抛出声明的异常；练习参考答案必须通过检查，起始代码必须不通过。
// 用法：npm run verify:pyodide [-- 关键字]
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createRequire } from 'node:module'
import { parseInfo, parseExercise } from '../.vitepress/lib/blocks.mjs'

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const docs = path.resolve(siteRoot, '../docs')
const filter = process.argv[2] || ''
const require = createRequire(import.meta.url)
const { loadPyodide } = await import('pyodide')

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = path.join(dir, e.name)
    return e.isDirectory() ? walk(p) : e.name.endsWith('.md') ? [p] : []
  })
}

function blocks(file) {
  const out = []
  const lines = fs.readFileSync(file, 'utf8').split('\n')
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(`{3,})(.*)$/)
    if (!m) continue
    const fence = m[1]
    const info = parseInfo(m[2])
    const start = i + 1
    const body = []
    for (i++; i < lines.length && !lines[i].startsWith(fence); i++) body.push(lines[i])
    if (info.lang === 'python') out.push({ line: start, info, content: body.join('\n') + '\n' })
  }
  return out
}

const py = await loadPyodide({ indexURL: path.dirname(require.resolve('pyodide/package.json')) })
py.runPython(fs.readFileSync(path.join(siteRoot, 'public/py-runtime.py'), 'utf8'))
const run = py.globals.get('course_run')
const version = py.runPython('import sys; sys.version.split()[0]')
const exec = (code, check = '') => {
  const r = run(code, check)
  const o = r.toJs({ dict_converter: Object.fromEntries })
  r.destroy()
  return o
}

const stats = { examples: 0, solutions: 0, starters: 0 }
const failures = []
const files = walk(docs).filter((f) => f.includes(filter)).sort()
for (const file of files) {
  const rel = path.relative(path.resolve(docs, '..'), file)
  for (const b of blocks(file)) {
    const where = `${rel}:${b.line}`
    if (b.info.flags.has('run')) {
      const r = exec(b.content)
      const want = b.info.attrs.raises
      const good = want ? !r.ok && r.errType === want && r.phase === 'code' : r.ok
      if (good) stats.examples++
      else failures.push(`${where} 示例${want ? `（预期 ${want}）` : ''}：${(r.err || '意外成功').trim().split('\n').slice(-3).join(' | ')}`)
    } else if (b.info.flags.has('exercise')) {
      const ex = parseExercise(b.content)
      const id = b.info.attrs.id
      const s = exec(ex.solution, ex.check)
      if (s.ok) stats.solutions++
      else failures.push(`${where} 练习 ${id} 参考答案未通过：${s.err.trim().split('\n').slice(-3).join(' | ')}`)
      const t = exec(ex.starter, ex.check)
      if (!t.ok) stats.starters++
      else failures.push(`${where} 练习 ${id} 起始代码竟然通过了检查`)
    }
  }
}

console.log(`Pyodide 内 Python ${version}；扫描 ${files.length} 个文件`)
console.log(`示例通过 ${stats.examples}，参考答案通过 ${stats.solutions}，起始代码被判失败 ${stats.starters}`)
if (failures.length) {
  console.log(`\n失败 ${failures.length} 项：`)
  for (const f of failures) console.log('  ✗ ' + f)
  process.exit(1)
}
console.log('全部通过 ✅')

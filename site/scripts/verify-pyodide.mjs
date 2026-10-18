// 在 Node 中用 Pyodide（与浏览器相同的运行时与 py-runtime.py）执行全部课程代码块：
//   示例（run）必须正常结束或抛出声明的异常；练习参考答案必须通过检查，起始代码必须不通过。
//   `python local` 跳过（仅本地 CPython）；单块默认 20s 超时。
// 用法：npm run verify:pyodide [-- 关键字]
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { Worker } from 'node:worker_threads'
import { parseInfo, parseExercise } from '../.vitepress/lib/blocks.mjs'

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const docs = path.resolve(siteRoot, '../docs')
const filter = process.argv[2] || ''
const BLOCK_TIMEOUT_MS = parseInt(process.env.PYODIDE_BLOCK_TIMEOUT_MS || '20000', 10)

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

let workerSeq = 0
let pyVersion = '?'
let worker = null
const pending = new Map()
let readyWait = null

function bootWorker() {
  worker = new Worker(new URL('./verify-pyodide-worker.mjs', import.meta.url))
  readyWait = new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('Pyodide Worker 启动超时')), 120_000)
    worker.once('message', (msg) => {
      if (msg.type !== 'ready') return
      clearTimeout(t)
      pyVersion = msg.version
      resolve()
    })
  })
  worker.on('message', (msg) => {
    if (msg.type === 'result') {
      const p = pending.get(msg.id)
      if (!p) return
      clearTimeout(p.timer)
      pending.delete(msg.id)
      p.resolve(msg)
    }
  })
  worker.on('error', (e) => {
    for (const [, p] of pending) {
      clearTimeout(p.timer)
      p.resolve({ ok: false, err: String(e.message || e), phase: 'runtime' })
    }
    pending.clear()
  })
}

bootWorker()

async function execTimed(code, check = '') {
  await readyWait
  return new Promise((resolve) => {
    const id = ++workerSeq
    const timer = setTimeout(async () => {
      pending.delete(id)
      try {
        worker.terminate()
      } catch {
        /* ignore */
      }
      bootWorker()
      await readyWait
      resolve({
        ok: false,
        err: `单块超时（${BLOCK_TIMEOUT_MS}ms）`,
        phase: 'timeout',
        errType: 'Timeout',
      })
    }, BLOCK_TIMEOUT_MS)
    pending.set(id, { resolve, timer })
    worker.postMessage({ type: 'run', id, code, check })
  })
}

await readyWait

const stats = { examples: 0, solutions: 0, starters: 0, skippedLocal: 0 }
const failures = []
const files = walk(docs).filter((f) => f.includes(filter)).sort()
for (const file of files) {
  const rel = path.relative(path.resolve(docs, '..'), file)
  for (const b of blocks(file)) {
    const where = `${rel}:${b.line}`
    if (b.info.flags.has('local')) {
      stats.skippedLocal++
      continue
    }
    if (b.info.flags.has('run')) {
      const r = await execTimed(b.content)
      const want = b.info.attrs.raises
      const good = want ? !r.ok && r.errType === want && r.phase === 'code' : r.ok
      if (good) stats.examples++
      else {
        const hint = r.phase === 'timeout' ? `超时 @ ${where}` : (r.err || '意外成功').trim().split('\n').slice(-3).join(' | ')
        failures.push(`${where} 示例${want ? `（预期 ${want}）` : ''}：${hint}`)
      }
    } else if (b.info.flags.has('exercise') && b.info.flags.has('local')) {
      stats.skippedLocal++
    } else if (b.info.flags.has('exercise')) {
      const ex = parseExercise(b.content)
      const id = b.info.attrs.id
      const s = await execTimed(ex.solution, ex.check)
      if (s.ok) stats.solutions++
      else failures.push(`${where} 练习 ${id} 参考答案未通过：${s.err?.trim().split('\n').slice(-3).join(' | ')}`)
      const t = await execTimed(ex.starter, ex.check)
      if (!t.ok) stats.starters++
      else failures.push(`${where} 练习 ${id} 起始代码竟然通过了检查`)
    }
  }
}

try {
  worker.terminate()
} catch {
  /* ignore */
}

console.log(`Pyodide 内 Python ${pyVersion}；扫描 ${files.length} 个文件；跳过 local ${stats.skippedLocal} 块`)
console.log(`示例通过 ${stats.examples}，参考答案通过 ${stats.solutions}，起始代码被判失败 ${stats.starters}`)
if (failures.length) {
  console.log(`\n失败 ${failures.length} 项：`)
  for (const f of failures) console.log('  ✗ ' + f)
  process.exit(1)
}
console.log('全部通过 ✅')

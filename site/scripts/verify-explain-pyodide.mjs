// CPython 与 Pyodide 对 py-explain 输出逐 JSON 字符串对比（E02）；含 P95 性能（E09）。
import fs from 'node:fs'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { createRequire } from 'node:module'

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const projectRoot = path.resolve(siteRoot, '..')
const benchOnly = process.argv.includes('--bench')

function pyJsonExplain(source, filename) {
  const script = path.join(siteRoot, 'public/py-explain.py')
  const tmpDir = fs.mkdtempSync(path.join(projectRoot, '.run/explain-'))
  const safe = (filename || 'snippet.py').replace(/[^a-zA-Z0-9._-]/g, '_')
  const f = path.join(tmpDir, safe.endsWith('.py') ? safe : `${safe}.py`)
  fs.writeFileSync(f, source)
  const proc = spawnSync('uv', ['run', 'python', script, '--cli', f], { cwd: projectRoot, encoding: 'utf8' })
  fs.rmSync(tmpDir, { recursive: true, force: true })
  if (proc.status !== 0) throw new Error(proc.stderr || proc.stdout || 'cli failed')
  return proc.stdout.trim()
}

function collectCorpusViaPython() {
  const code = `
import json, sys
sys.path.insert(0, ${JSON.stringify(path.join(projectRoot, 'tests'))})
from check_explain import collect_corpus
items, stats = collect_corpus()
out = [{"label": a, "filename": b, "source": c} for a, b, c in items]
print(json.dumps({"items": out, "stats": stats}, ensure_ascii=False))
`
  const proc = spawnSync('uv', ['run', 'python', '-c', code], { cwd: projectRoot, encoding: 'utf8', maxBuffer: 80 * 1024 * 1024 })
  if (proc.status !== 0) throw new Error(proc.stderr || 'corpus failed')
  return JSON.parse(proc.stdout)
}

async function bootExplainWorker() {
  const require = createRequire(import.meta.url)
  const { loadPyodide } = await import('pyodide')
  const py = await loadPyodide({ indexURL: path.dirname(require.resolve('pyodide/package.json')) })
  const conceptMd = fs.readFileSync(path.join(projectRoot, 'docs/代码解读/概念索引.md'), 'utf8')
  py.FS.writeFile('/concept-index.md', conceptMd)
  py.runPython(fs.readFileSync(path.join(siteRoot, 'public/py-explain.py'), 'utf8'))
  py.runPython("configure('/concept-index.md')")
  return py
}

function pyodideJsonExplain(py, source, filename) {
  py.globals.set('_explain_src', source)
  py.globals.set('_explain_fn', filename)
  return py.runPython(`import json; json.dumps(course_explain(_explain_src, _explain_fn), ensure_ascii=False)`)
}

async function main() {
  const { items } = collectCorpusViaPython()
  const py = await bootExplainWorker()
  let mismatches = 0
  const samples = []
  if (!benchOnly) {
    for (const item of items) {
      const fn = item.filename.includes('/') ? item.filename.split('/').pop() : item.filename
      const name = fn && fn.endsWith('.py') ? fn : '<input>'
      let pyOut
      let jsOut
      try {
        pyOut = pyJsonExplain(item.source, name)
        jsOut = pyodideJsonExplain(py, item.source, name)
      } catch (e) {
        mismatches++
        if (samples.length < 3) samples.push(`${item.label}: ${e}`)
        continue
      }
      if (pyOut !== jsOut) {
        mismatches++
        if (samples.length < 3) samples.push(`${item.label}: 字节不一致 (Δ len ${pyOut.length - jsOut.length})`)
      }
    }
    if (mismatches > 0) {
      console.error(`E02: ${mismatches}/${items.length} 不一致`)
      for (const s of samples) console.error('  ', s)
      process.exit(1)
    }
    console.log(`E02: ${items.length}/${items.length} 语料 JSON 逐字节一致`)
  }

  const minimal = fs.readFileSync(path.join(projectRoot, 'examples/agent/minimal_agent.py'), 'utf8')
  const big = `${minimal}\n# pad\n${'x = 1\n'.repeat(2950)}`
  pyodideJsonExplain(py, 'pass\n', 'w.py')

  const timeRuns = (source, filename, n) => {
    const ms = []
    for (let i = 0; i < n; i++) {
      const t0 = performance.now()
      pyodideJsonExplain(py, source, filename)
      ms.push(performance.now() - t0)
    }
    ms.sort((a, b) => a - b)
    return ms[Math.min(ms.length - 1, Math.ceil(n * 0.95) - 1)]
  }
  const p95Mini = timeRuns(minimal, 'minimal_agent.py', 20)
  const p95Big = timeRuns(big, 'big.py', 20)
  console.log(`E09: minimal_agent P95 ${Math.round(p95Mini)} ms; 3000 行 P95 ${Math.round(p95Big)} ms`)
  if (p95Mini > 150 || p95Big > 1500) {
    console.error('E09: 超出门槛')
    process.exit(1)
  }
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})

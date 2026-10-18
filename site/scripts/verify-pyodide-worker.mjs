// 在 Worker 中加载 Pyodide 并执行单个代码块（供 verify-pyodide.mjs 做单块超时）。
import fs from 'node:fs'
import path from 'node:path'
import { parentPort } from 'node:worker_threads'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const require = createRequire(import.meta.url)
const { loadPyodide } = await import('pyodide')

const py = await loadPyodide({ indexURL: path.dirname(require.resolve('pyodide/package.json')) })
py.runPython(fs.readFileSync(path.join(siteRoot, 'public/py-runtime.py'), 'utf8'))
const run = py.globals.get('course_run')
const version = py.runPython('import sys; sys.version.split()[0]')

parentPort.postMessage({ type: 'ready', version })

parentPort.on('message', (data) => {
  if (data.type !== 'run') return
  try {
    const r = run(data.code, data.check || '')
    const o = r.toJs({ dict_converter: Object.fromEntries })
    r.destroy()
    parentPort.postMessage({ type: 'result', id: data.id, ...o })
  } catch (e) {
    parentPort.postMessage({
      type: 'result',
      id: data.id,
      ok: false,
      out: '',
      err: String(e?.message || e),
      phase: 'runtime',
    })
  }
})

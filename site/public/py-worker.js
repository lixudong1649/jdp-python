// Pyodide Web Worker（模块 Worker）。优先加载本地 /pyodide/（离线可用），失败时回退官方 CDN。
const PYODIDE_VERSION = '314.0.7'
const CDN = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`
const base = new URL(self.location.href).searchParams.get('base') || '/'

async function boot() {
  let mod
  let indexURL = new URL(base + 'pyodide/', self.location.origin).href
  let source = 'local'
  try {
    mod = await import(indexURL + 'pyodide.mjs')
  } catch (e) {
    indexURL = CDN
    source = 'cdn'
    mod = await import(CDN + 'pyodide.mjs')
  }
  const py = await mod.loadPyodide({ indexURL })
  const helper = await (await fetch(new URL(base + 'py-runtime.py', self.location.origin))).text()
  py.runPython(helper)
  const explainSrc = await (await fetch(new URL(base + 'py-explain.py', self.location.origin))).text()
  py.runPython(explainSrc)
  try {
    const conceptMd = await (await fetch(new URL(base + 'concept-index.md', self.location.origin))).text()
    py.FS.writeFile('/concept-index.md', conceptMd)
    py.runPython("configure('/concept-index.md')")
  } catch (_) {
    /* 概念索引可选 */
  }
  const version = py.runPython('import sys; sys.version.split()[0]')
  const run = py.globals.get('course_run')
  const explainFn = py.globals.get('course_explain')
  return { py, run, explainFn, source, version }
}

const ready = boot()
ready.then(
  (r) => postMessage({ type: 'ready', source: r.source, python: r.version, pyodide: PYODIDE_VERSION }),
  (e) => postMessage({ type: 'fatal', error: String(e && e.message || e) }),
)

self.onmessage = async ({ data }) => {
  const ctx = await ready
  if (data.type === 'run') {
    postMessage({ type: 'start', id: data.id })
    try {
      const res = ctx.run(data.code, data.check || '')
      const obj = res.toJs({ dict_converter: Object.fromEntries })
      res.destroy()
      postMessage({ type: 'result', id: data.id, ...obj })
    } catch (e) {
      postMessage({ type: 'result', id: data.id, ok: false, out: '', err: String(e && e.message || e), phase: 'runtime' })
    }
    return
  }
  if (data.type === 'explain') {
    postMessage({ type: 'start', id: data.id })
    try {
      const res = ctx.explainFn(data.code, data.filename || '<input>')
      const obj = res.toJs({ dict_converter: Object.fromEntries })
      res.destroy()
      postMessage({ type: 'explain-result', id: data.id, result: obj })
    } catch (e) {
      postMessage({
        type: 'explain-result',
        id: data.id,
        result: { ok: false, error: { line: 1, column: 0, message: String(e && e.message || e) } },
      })
    }
  }
}

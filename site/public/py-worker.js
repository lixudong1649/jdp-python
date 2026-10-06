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
  const version = py.runPython('import sys; sys.version.split()[0]')
  return { py, run: py.globals.get('course_run'), source, version }
}

const ready = boot()
ready.then(
  (r) => postMessage({ type: 'ready', source: r.source, python: r.version, pyodide: PYODIDE_VERSION }),
  (e) => postMessage({ type: 'fatal', error: String(e && e.message || e) }),
)

self.onmessage = async ({ data }) => {
  if (data.type !== 'run') return
  const { run } = await ready
  postMessage({ type: 'start', id: data.id })
  try {
    const res = run(data.code, data.check || '')
    const obj = res.toJs({ dict_converter: Object.fromEntries })
    res.destroy()
    postMessage({ type: 'result', id: data.id, ...obj })
  } catch (e) {
    postMessage({ type: 'result', id: data.id, ok: false, out: '', err: String(e && e.message || e), phase: 'runtime' })
  }
}

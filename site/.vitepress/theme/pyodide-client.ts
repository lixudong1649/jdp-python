import { ref } from 'vue'
import { withBase } from 'vitepress'

export interface RunResult {
  ok: boolean
  out: string
  err: string
  errType?: string
  phase?: string
  ms?: number
  python?: string
  timeout?: boolean
}

export type Status = 'idle' | 'loading' | 'ready' | 'error'
export const status = ref<Status>('idle')
export const runtimeInfo = ref('')

const TIMEOUT_MS = 10_000
let worker: Worker | null = null
let seq = 0
const pending = new Map<number, { resolve: (r: RunResult) => void; timer?: number }>()

function spawn(): Worker {
  status.value = 'loading'
  const w = new Worker(withBase('/py-worker.js') + '?base=' + encodeURIComponent(withBase('/')), { type: 'module' })
  w.onmessage = ({ data }) => {
    if (data.type === 'ready') {
      status.value = 'ready'
      runtimeInfo.value = `Python ${data.python} · Pyodide ${data.pyodide}（${data.source === 'local' ? '本地' : 'CDN'}）`
    } else if (data.type === 'fatal') {
      status.value = 'error'
      runtimeInfo.value = `Python 运行时加载失败：${data.error}`
      for (const [, p] of pending) p.resolve({ ok: false, out: '', err: runtimeInfo.value, phase: 'runtime' })
      pending.clear()
    } else if (data.type === 'start') {
      const p = pending.get(data.id)
      if (p) p.timer = window.setTimeout(() => kill(data.id), TIMEOUT_MS)
    } else if (data.type === 'result') {
      const p = pending.get(data.id)
      if (!p) return
      clearTimeout(p.timer)
      pending.delete(data.id)
      const { type, id, ...rest } = data
      p.resolve(rest as RunResult)
    }
  }
  w.onerror = (e) => {
    status.value = 'error'
    runtimeInfo.value = `Worker 错误：${e.message}`
  }
  return w
}

function kill(id: number) {
  worker?.terminate()
  worker = null
  status.value = 'idle'
  for (const [pid, p] of pending) {
    clearTimeout(p.timer)
    p.resolve({
      ok: false,
      out: '',
      err: pid === id ? `运行超过 ${TIMEOUT_MS / 1000} 秒已被终止（可能是死循环）。运行时将在下次运行时重新加载。` : '运行被中断',
      phase: 'timeout',
      timeout: true,
    })
  }
  pending.clear()
}

/** 预热：页面出现可运行代码块时提前加载运行时。 */
export function warmup() {
  if (!worker) worker = spawn()
}

export function runPython(code: string, check = ''): Promise<RunResult> {
  if (!worker) worker = spawn()
  const id = ++seq
  return new Promise((resolve) => {
    pending.set(id, { resolve })
    worker!.postMessage({ type: 'run', id, code, check })
  })
}

export function b64decode(s: string): string {
  const bin = atob(s)
  const bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0))
  return new TextDecoder().decode(bytes)
}

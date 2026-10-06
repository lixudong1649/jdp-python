// 课程 Markdown 代码块约定（与 tests/check_course.py 保持一致）：
//   ```python run                      可运行示例，必须无异常结束
//   ```python run raises=TypeError     可运行示例，预期抛出指定异常（演示报错）
//   ```python exercise id=<唯一ID>      练习：内部用 starter / solution / check 三段分隔
//   ```python fragment                 片段，仅展示，不做语法检查
//   ```python                          静态代码，仅展示（校验器会做语法检查）

export const SECTION_RE = /^# --- (starter|solution|check) ---\s*$/

export function parseInfo(info) {
  const parts = (info || '').trim().split(/\s+/).filter(Boolean)
  const lang = parts.shift() || ''
  const flags = new Set()
  const attrs = {}
  for (const p of parts) {
    const i = p.indexOf('=')
    if (i > 0) attrs[p.slice(0, i)] = p.slice(i + 1)
    else flags.add(p)
  }
  return { lang, flags, attrs }
}

export function parseExercise(content) {
  const out = { starter: '', solution: '', check: '' }
  let cur = null
  const buf = { starter: [], solution: [], check: [] }
  for (const line of content.split('\n')) {
    const m = line.match(SECTION_RE)
    if (m) { cur = m[1]; continue }
    if (cur) buf[cur].push(line)
  }
  for (const k of Object.keys(buf)) out[k] = buf[k].join('\n').replace(/^\n+|\s+$/g, '') + '\n'
  return out
}

export function toB64(s) {
  return Buffer.from(s, 'utf8').toString('base64')
}

import path from 'node:path'
import { parseInfo, parseExercise, toB64 } from './blocks.mjs'

const escAttr = (s) => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;')

/**
 * markdown-it 插件：
 * 1. 把 `python run` / `python exercise` 代码块渲染为交互组件（静态高亮作为无 JS 时的回退内容）；
 * 2. 把指向 docs/ 之外的相对链接（如 ../examples/agent/minimal_agent.py）改写为 /repo/<路径>.txt 纯文本副本。
 */
export function coursePlugin(md, { srcDir, projectRoot }) {
  const fence = md.renderer.rules.fence
  md.renderer.rules.fence = (tokens, idx, options, env, self) => {
    const t = tokens[idx]
    const info = parseInfo(t.info)
    if (info.lang === 'python' && info.flags.has('run')) {
      t.info = 'python'
      const fallback = fence(tokens, idx, options, env, self)
      const raises = info.attrs.raises ? ` raises="${escAttr(info.attrs.raises)}"` : ''
      return `<PyRunner code="${toB64(t.content)}"${raises}>${fallback}</PyRunner>\n`
    }
    if (info.lang === 'python' && info.flags.has('exercise')) {
      const ex = parseExercise(t.content)
      const id = info.attrs.id || `ex-${idx}`
      return `<PyExercise ex-id="${escAttr(id)}" data="${toB64(JSON.stringify(ex))}"></PyExercise>\n`
    }
    if (info.lang === 'python' && info.flags.size) t.info = 'python'
    return fence(tokens, idx, options, env, self)
  }

  md.core.ruler.push('course_outside_links', (state) => {
    const file = state.env && state.env.path
    if (!file) return
    const walk = (tokens) => {
      for (const tok of tokens) {
        if (tok.children) walk(tok.children)
        if (tok.type !== 'link_open') continue
        const href = tok.attrGet('href') || ''
        if (/^([a-z]+:|#|\/)/i.test(href)) continue
        const [p, hash] = href.split('#')
        const abs = path.resolve(path.dirname(file), decodeURI(p))
        if (abs.startsWith(srcDir + path.sep)) continue
        const rel = path.relative(projectRoot, abs).split(path.sep).join('/')
        tok.attrSet('href', `/repo/${encodeURI(rel)}.txt${hash ? '#' + hash : ''}`)
        tok.attrSet('target', '_blank')
      }
    }
    walk(state.tokens)
  })
}

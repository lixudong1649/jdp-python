import fs from 'node:fs'
import path from 'node:path'

export function frontmatter(file) {
  const src = fs.readFileSync(file, 'utf8')
  const m = src.match(/^---\n([\s\S]*?)\n---/)
  const fm = {}
  if (m) {
    for (const line of m[1].split('\n')) {
      const i = line.indexOf(':')
      if (i > 0) fm[line.slice(0, i).trim()] = line.slice(i + 1).trim().replace(/^['"]|['"]$/g, '')
    }
  }
  if (!fm.title) {
    const h = src.match(/^#\s+(.+)$/m)
    if (h) fm.title = h[1].trim()
  }
  return fm
}

/** 扫描 docs/课程/NN-阶段/ 目录，生成阶段与课程元数据（侧边栏、首页路线图、进度统计共用）。 */
export function loadCourse(srcDir) {
  const root = path.join(srcDir, '课程')
  const stages = []
  for (const dir of fs.readdirSync(root).sort()) {
    const m = dir.match(/^(\d\d)-(.+)$/)
    if (!m || !fs.statSync(path.join(root, dir)).isDirectory()) continue
    const idx = path.join(root, dir, 'index.md')
    const fm = fs.existsSync(idx) ? frontmatter(idx) : {}
    const lessons = fs.readdirSync(path.join(root, dir))
      .filter((f) => /^\d\d-.+\.md$/.test(f))
      .sort()
      .map((f) => ({
        title: frontmatter(path.join(root, dir, f)).title || f,
        link: `/课程/${dir}/${f.replace(/\.md$/, '')}`,
      }))
    stages.push({
      no: Number(m[1]),
      title: fm.title || m[2],
      short: m[2],
      goal: fm.goal || '',
      link: `/课程/${dir}/`,
      lessons,
    })
  }
  return stages
}

export function buildSidebar(stages, srcDir) {
  const exists = (p) => fs.existsSync(path.join(srcDir, p))
  const guide = [
    { text: '课程首页', link: '/' },
    { text: '课程大纲', link: '/课程大纲' },
    { text: '学习路线', link: '/学习路线' },
    { text: 'Python 概览与环境', link: '/Python概览与环境' },
  ].filter((i) => i.link === '/' || exists(i.link.slice(1) + '.md'))
  const appendix = [
    { text: '速查表', link: '/课程/附录/速查表' },
    { text: '术语表', link: '/课程/附录/术语表' },
    { text: 'minimal_agent.py 语法速查', link: '/代码解读/minimal_agent' },
  ].filter((i) => exists(i.link.slice(1) + '.md'))
  return [
    { text: '开始', items: guide },
    ...stages.map((s) => ({
      text: `${s.no}. ${s.short}`,
      collapsed: true,
      items: [{ text: '阶段导读', link: s.link }, ...s.lessons.map((l) => ({ text: l.title, link: l.link }))],
    })),
    { text: '附录', items: appendix },
  ]
}

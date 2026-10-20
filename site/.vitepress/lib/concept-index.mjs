import fs from 'node:fs'
import path from 'node:path'

/** 解析 docs/代码解读/概念索引.md 表格行。 */
export function parseConceptIndexFile(filePath) {
  if (!fs.existsSync(filePath)) return []
  const rows = []
  for (const line of fs.readFileSync(filePath, 'utf8').split('\n')) {
    if (!line.startsWith('|') || line.startsWith('| ---')) continue
    const parts = line
      .trim()
      .slice(1, -1)
      .split('|')
      .map((p) => p.trim())
    if (parts.length < 6 || parts[0] === '概念 id' || !parts[0]) continue
    const linksFrom = (cell) => [...cell.matchAll(/\]\(([^)]+)\)/g)].map((m) => m[1])
    rows.push({
      id: parts[0],
      name: parts[1],
      ast: parts[2],
      meaning: parts[3],
      course: parts[4],
      glossary: parts[5],
      course_links: linksFrom(parts[4]),
      glossary_links: linksFrom(parts[5]),
    })
  }
  return rows
}

/** 写入 public/concept-index.json 并复制 .md 供 Pyodide 读取。 */
export function writeConceptIndexAssets(projectRoot, sitePublicDir) {
  const src = path.join(projectRoot, 'docs/代码解读/概念索引.md')
  const rows = parseConceptIndexFile(src)
  fs.mkdirSync(sitePublicDir, { recursive: true })
  fs.writeFileSync(path.join(sitePublicDir, 'concept-index.json'), JSON.stringify({ rows }, null, 0))
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, path.join(sitePublicDir, 'concept-index.md'))
  }
  return rows.length
}
